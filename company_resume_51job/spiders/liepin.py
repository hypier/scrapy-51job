# -*- coding: utf-8 -*-
import os
import time

import scrapy
from scrapy_redis.spiders import RedisSpider

from company_resume_51job.items import Job51Item
from urllib import parse


class LiePinJobSpider(RedisSpider):
    name = "liepin"
    allowed_domains = ["liepin.com"]
    redis_key = 'liepin:start_urls'

    # 基地址,循环城市,月薪,学历
    base_urls = 'https://www.liepin.com/zhaopin/?dqs=040&pubTime=3&salary=15%2430&jobKind=2&key=' \
                '&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7EQOW2X0Xbppe0Z4qiqak10A' \
                '&d_ckId=cc502ce88c9359b584e6652377441fe0&curPage=0' \
                '&d_headId=68157ae90a6cf93bf719f88942c26881&time{}'.format(time.strftime("%Y%m%d", time.localtime()))

    def parse(self, response):
        yield scrapy.Request(url=self.base_urls, callback=self.page1_parse, dont_filter=True)

    # 提取职位url,如果页码大于1,生成所有页码的请求加入队列
    def page1_parse(self, response):
        position = response.xpath('//ul[@class="sojob-list"]//div[@class="job-info"]//h3//a/@href').extract()
        if position is not None:
            for posi_url in position:
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, dont_filter=False)

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
                        yield scrapy.Request(url=next_url, callback=self.pages_parse)

    # 页码大于1的页面处理函数
    def pages_parse(self, response):
        position = response.xpath('//ul[@class="sojob-list"]//div[@class="job-info"]//h3//a/@href').extract()
        if position is not None:
            for posi_url in position:
                yield scrapy.Request(url=posi_url, callback=self.detail_parse, priority=1, dont_filter=False)

    # 职位详情页
    def detail_parse(self, response):

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

        job['info'] = '\n'.join(posi_info).strip()
        # 上班地址
        job['local'] = response.xpath('//ul[@class="new-compintro"]/li/text()').re("公司地址：(.*)")[0]
        # 公司网址
        job['co_url'] = response.xpath('//div[@class="company-logo"]//a/@href').extract()[0]
        # 公司行业
        job['co_trade'] = response.xpath('//ul[@class="new-compintro"]/li/a/text()').extract()
        yield job
