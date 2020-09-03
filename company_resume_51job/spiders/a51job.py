# -*- coding: utf-8 -*-
import json
import os
import time
from urllib import parse

import scrapy
from scrapy_redis.spiders import RedisSpider
from company_resume_51job.items import Job51Item


class A51jobSpider(RedisSpider):
    name = "51job"
    allowed_domains = ["51job.com"]
    redis_key = '51job:start_urls'

    city = '060000'  # 重庆
    salary = '15000-30000'
    kds = ['java', r'技术总监', r'架构师', r'java 技术经理']

    # 基地址
    urls = ['https://search.51job.com/list/060000,000000,0100%252c2600'
            '%252c7500%252c7900,00,1,15000-30000,+,2,1.html?lang=c&postchannel=0000&'
            'workyear=03%252c04%252c05&cotype=99&degreefrom=99&jobterm=01&companysize=99'
            '&ord_field=0&dibiaoid=0&line=&welfare=']

    base_url = 'https://search.51job.com/list/{},000000,0000,00,1,{},{},2,1.html?lang=c' \
               '&postchannel=0000&workyear=99&cotype=99&degreefrom=03%252c04%252c05&jobterm=99&companysize=99' \
               '&ord_field=0&dibiaoid=0&line=&welfare='

    # 学历类别
    edu_type = ['大专'.encode('utf-8').decode('utf8'),
                '本科'.encode('utf-8').decode('utf8'),
                '硕士'.encode('utf-8').decode('utf8')]

    def start_requests(self):
        for kd in self.kds:
            self.urls.append(self.base_url.format(self.city, self.salary, parse.quote(kd)))

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse,
                                 headers={'Accept': 'application/json'}, dont_filter=True)

    def parse(self, response):
        obj = json.loads(response.text)
        position = obj["engine_search_result"]
        if position is not None:
            for posi in position:
                posi_url = posi['job_href']
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, dont_filter=False)
            page = int(obj['total_page'])
            if page != 1:
                for p in range(2, page + 1):
                    next_url = response.url.replace('1.html', str(p) + '.html')
                    yield scrapy.Request(url=next_url, callback=self.pages_parse,
                                         headers={'Accept': 'application/json'})

    # 页码大于1的页面处理函数
    def pages_parse(self, response):
        obj = json.loads(response.text)
        position = obj["engine_search_result"]
        for posi in position:
            posi_url = posi['job_href']
            yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, dont_filter=False)

    # 职位详情页
    def detail_parse(self, response):
        # 判断信息是否存在
        ifexists = lambda x: x[0] if x else ''

        job = Job51Item()
        # job id
        job['id'] = os.path.basename(response.url).split(".")[0]
        # job website
        job['website'] = self.name
        # job time
        job['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # job url
        job['url'] = response.url
        # 职位名称
        job['name'] = response.xpath('//div[@class="tHeader tHjob"]//h1//text()').extract()[0].strip()
        # 公司名称
        job['co_name'] = response.xpath('//p[@class="cname"]/a//text()').extract()[0].strip()
        # 区域
        job['area'] = response.xpath('//div[@class="tHeader tHjob"]//p[@class="msg ltype"]/text()').extract()[0].strip()
        # 工资
        job['salary'] = ifexists(response.xpath('//div[@class="tHeader tHjob"]//strong/text()').extract())
        # 所有要求
        # 其他要求
        otherq = ''
        all_require = response.xpath('//div[@class="tHeader tHjob"]//p[@class="msg ltype"]/text()').extract()
        for require in all_require:
            require = require.strip()
            if '经验'.encode("utf-8").decode('utf8') in require:
                job['exp'] = require
            elif require in self.edu_type:
                job['edu'] = require
            elif '人'.encode("utf-8").decode('utf8') in require:
                job['num'] = require
            elif '发布'.encode("utf-8").decode('utf8') in require:
                job['pub_time'] = require.replace('发布'.encode("utf-8").decode('utf8'), '')
            else:
                otherq = otherq + require + ' '
        job['otherq'] = otherq.strip()
        # 福利
        welfare = ' '
        fuli = response.xpath('//div[@class="tHeader tHjob"]//div[@class="jtag"]/div/span/text()').extract()
        for f in fuli:
            welfare = welfare + f + ' '
        job['welfare'] = welfare.strip()
        # 职位信息
        posi_info = response.xpath(
            '//div[@class="tBorderTop_box"][1]//div[@class="bmsg job_msg inbox"]/p//text()').extract()

        job['info'] = '\n'.join(posi_info)
        # 上班地址
        job['local'] = ifexists(
            response.xpath('//div[@class="tBorderTop_box"]/div[@class="bmsg inbox"]//p/text()').extract())
        # 公司网址
        job['co_url'] = response.xpath('//div[@class="tHeader tHjob"]//p[@class="cname"]/a/@href').extract()[0]
        # 公司类型
        job['co_type'] = response.xpath('//div[@class="tCompanyPage"]//div[@class="com_tag"]/p[1]/text()').extract()
        # 公司行业
        job['co_trade'] = response.xpath('//div[@class="tCompanyPage"]//div[@class="com_tag"]//p//'
                                         'span[@class="i_trade"]/following-sibling::a[1]/text()').extract()
        yield job
