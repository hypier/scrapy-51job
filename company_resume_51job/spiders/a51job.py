# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy_redis.spiders import RedisSpider
from company_resume_51job.items import Job51Item


class A51jobSpider(RedisSpider):
    name = "51job"
    allowed_domains = ["51job.com"]
    redis_key = '51job:start_urls'

    # 基地址,循环城市,月薪,学历
    base_urls = 'http://search.51job.com/list/%s,000000,0000,00,9,%s,%s,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=%s&jobterm=99&companysize=99&lonlat=0%s0&radius=-1&ord_field=0&confirmdate=9&fromType=1&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='

    # 获取城市列表
    city_list = ['092200']

    # 获取工资列表
    salary_list = ['08', '09', '10']

    # 学历列表
    edu_list = ['03', '04', '05']

    # 学历类别
    edu_type = ['大专'.encode('utf-8').decode('utf8'),
                '本科'.encode('utf-8').decode('utf8'),
                '硕士'.encode('utf-8').decode('utf8')]

    # 职位信息中不需要的信息
    unrequire = ['分享'.encode('utf-8').decode('utf8'), '微信'.encode('utf-8').decode('utf8'),
                 '邮件'.encode('utf-8').decode('utf8')]

    # 基于不同的城市,工资,学历的第一页请求
    def parse(self, response):
        for salaryid in self.salary_list:
            for eduid in self.edu_list:
                fullurl = self.base_urls % ('060000', salaryid, '%2B', eduid, '%2C')
                yield scrapy.Request(url=fullurl, callback=self.page1_parse, headers={'Accept': 'application/json'})

    # 提取职位url,如果页码大于1,生成所有页码的请求加入队列
    def page1_parse(self, response):
        obj = json.loads(response.text)
        position = obj["engine_search_result"]
        if position is not None:
            for posi in position:
                posi_url = posi['job_href']
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1)
            page = int(obj['total_page'])
            if page != 1:
                for p in range(2, page + 1):
                    next_url = response.url.replace('1.html', str(p) + '.html')
                    yield scrapy.Request(url=next_url, callback=self.pages_parse, headers={'Accept': 'application/json'})

    # 页码大于1的页面处理函数
    def pages_parse(self, response):
        obj = json.loads(response.text)
        position = obj["engine_search_result"]
        for posi in position:
            posi_url = posi['job_href']
            yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1)

    # 职位详情页
    def detail_parse(self, response):
        # 判断信息是否存在
        ifexists = lambda x: x[0] if x else ''
        job = Job51Item()
        # 职位名称
        job['name'] = response.xpath('//div[@class="tHeader tHjob"]//h1//text()').extract()[0]
        # 公司名称
        job['co_name'] = response.xpath('//p[@class="cname"]/a//text()').extract()[0]
        # 区域
        job['area'] = response.xpath('//div[@class="tHeader tHjob"]//span/text()').extract()[0]
        # 工资
        job['salary'] = ifexists(response.xpath('//div[@class="tHeader tHjob"]//strong/text()').extract())
        # 所有要求
        # 其他要求
        otherq = ''
        all_require = response.xpath('//div[@class="tBorderTop_box bt"]//div[@class="t1"]/span/text()').extract()
        for require in all_require:
            if '经验'.decode('utf8') in require:
                job['exp'] = require
            elif require in self.edu_type:
                job['edu'] = require
            elif '人'.decode('utf8') in require:
                job['num'] = require
            elif '发布'.decode('utf8') in require:
                job['time'] = require
            else:
                otherq = otherq + require + ' '
        job['otherq'] = otherq
        # 福利
        welfare = ' '
        fuli = response.xpath('//div[@class="tBorderTop_box bt"]//p[@class="t2"]/span/text()').extract()
        for f in fuli:
            welfare = welfare + f + ' '
        job['welfare'] = welfare
        # 职位信息
        posi_info = response.xpath(
            '//div[@class="tBorderTop_box"][1]//div[@class="bmsg job_msg inbox"]//text()').extract()
        for i in posi_info:
            if i in self.unrequire:
                posi_info.remove(i)
            else:
                i.strip()
        job['info'] = ' '.join(posi_info)
        # 上班地址
        job['local'] = ifexists(
            response.xpath('//div[@class="tBorderTop_box"]/div[@class="bmsg inbox"]//p/text()[2]').extract())
        # 公司网址
        job['co_url'] = response.xpath('//div[@class="tHeader tHjob"]//p[@class="cname"]/a/@href').extract()[0]
        # 公司类型
        str1 = response.xpath('//div[@class="tHeader tHjob"]//p[@class="msg ltype"]/text()').extract()[0]
        strtotal = ''
        strlist = str1.split('|')
        for s in strlist:
            strtotal = strtotal + s.strip() + '|'
        job['co_type'] = strtotal
        yield job
