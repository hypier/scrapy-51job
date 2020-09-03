# -*- coding: utf-8 -*-
import os
import time
import uuid
from urllib.parse import quote, unquote

import scrapy
from scrapy_redis.spiders import RedisSpider

from company_resume_51job.items import Job51Item
from urllib import parse


class LiePinJobSpider(RedisSpider):
    name = "liepin"
    allowed_domains = ["liepin.com"]
    redis_key = 'liepin:start_urls'
    start_urls = 'http://www.liepin.com'

    # 基地址
    base_urls = 'https://www.liepin.com/zhaopin/?dqs=040&pubTime=3&salary=15%2430&jobKind=2&key={}&curPage=0'

    keys = ['java'.encode('utf-8').decode('utf8'),
            '架构师'.encode('utf-8').decode('utf8'),
            '技术总监'.encode('utf-8').decode('utf8'),
            'java 技术经理'.encode('utf-8').decode('utf8')]

    def get_cookie(self):
        uid = str(uuid.uuid4())
        suid = ''.join(uid.split('-'))
        return {'JSESSIONID': suid, 'Domain': 'www.liepin.com', 'Path': '/'}

    def start_requests(self):
        for key in self.keys:
            full_url = self.base_urls.format(quote(key))
            yield scrapy.Request(url=full_url, callback=self.parse, dont_filter=True, cookies=self.get_cookie())

    def parse(self, response):
        position = response.xpath('//ul[@class="sojob-list"]//div[@class="job-info"]//h3//a/@href').extract()
        if position is not None:
            for posi_url in position:
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, cookies=self.get_cookie())

            str_page = response.xpath('//div[@class="sojob-result "]//a[@class="last"]/@href').extract()
            if len(str_page) > 0:
                url = str_page[0]
                params = list(parse.urlparse(url))
                qs = parse.parse_qs(params[4])
                page = int(qs['curPage'][0])
                if page != 0:
                    for p in range(1, page):
                        qs['curPage'] = [p]
                        params[4] = parse.urlencode(qs, True)
                        next_url = parse.urljoin("https://www.liepin.com/zhaopin/", parse.urlunparse(params))
                        print(next_url)
                        yield scrapy.Request(url=next_url, callback=self.pages_parse, cookies=self.get_cookie())

    # 页码大于1的页面处理函数
    def pages_parse(self, response):
        position = response.xpath('//ul[@class="sojob-list"]//div[@class="job-info"]//h3//a/@href').extract()
        if position is not None:
            for posi_url in position:
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, dont_filter=False,
                                     cookies=self.get_cookie())

    # 职位详情页
    def detail_parse(self, response):

        job = Job51Item()
        # job id
        job['id'] = os.path.basename(response.url).split(".")[0]
        # job website
        job['website'] = self.name
        # job time
        job['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        job['pub_time'] = time.strftime('%m-%d', time.localtime(time.time()))
        # job url
        job['url'] = response.url
        # 职位名称
        job['name'] = response.xpath('//div[@class="title-info"]//h1//text()').extract()[0].strip()
        # 公司名称
        job['co_name'] = response.xpath('//div[@class="title-info"]//h3//a/text()').extract()[0].strip()
        # 区域
        job['area'] = response.xpath('//p[@class="basic-infor"]//a/text()').extract()[0].strip()
        # 工资
        job['salary'] = response.xpath('//p[@class="job-item-title"]/text()').extract()[0].strip()
        # 所有要求
        # 其他要求
        all_require = response.xpath('//div[@class="job-qualifications"]/span/text()').extract()

        job['exp'] = all_require[1]
        job['edu'] = all_require[0]
        job['otherq'] = all_require[2] + ' ' + all_require[3]

        # 福利
        welfare = ' '
        fuli = response.xpath('//ul[@class="comp-tag-list clearfix"]/li/span/text()').extract()
        for f in fuli:
            welfare = welfare + f + ' '
        job['welfare'] = welfare.strip()
        # 职位信息
        posi_info = response.xpath('//div[@class="content content-word"]/text()').extract()

        job['info'] = ''.join(posi_info).strip()
        # 上班地址
        local = response.xpath('//ul[@class="new-compintro"]/li/text()').re("公司地址：(.*)")
        if len(local) > 0:
            job['local'] = local
        # 公司网址
        job['co_url'] = response.xpath('//div[@class="company-logo"]//a/@href').extract()[0]
        # 公司行业
        job['co_trade'] = response.xpath('//ul[@class="new-compintro"]/li/a/text()').extract()
        yield job
