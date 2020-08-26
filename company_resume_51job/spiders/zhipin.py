import os
import time
from urllib import parse

import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy_splash import SplashRequest
from company_resume_51job.items import Job51Item


class JobSpider(RedisSpider):
    # spider的名字定义了Scrapy如何定位（并初始化）spider，所以其必须是唯一的。不过您可以生成多个相同的spider实例（instance），这没有任何限制。name是spider最重要的属性，而且是必须的
    name = 'zhipin'

    # 可选。包含了spider允许爬取的域名（domain）列表（list）。当OffsiteMiddleware启用时，域名不在列表中的URL不会被跟进。
    allowed_domains = ['www.zhipin.com']

    # URL列表。当没有制定特定的URL时，spider将从该列表中开始进行爬取。
    # 这里我们进行了指定，所以不是从这个URL列表里爬取
    start_urls = ['https://www.zhipin.com']

    headers = {
        'accept-encoding': 'deflate',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9'
    }

    cookies = {
        "__zp_stoken__": "ad34bWChTGV48cjpDLms%2FeANRWwRFUHhBRS4qDkduJlVCLk0jQX8Vf0wINVFHOnZ5LXsSQD8JHRd%2FeDo1IiN6"
                         "dUEuUXwWZkI4fGUKK2dAC1kNI194CWEVAAsHIxF%2BIykrKypvJn99YGxUBXJWOQ%3D%3D"
    }

    # 该方法必须返回一个可迭代对象(iterable)。该对象包含了spider用于爬取的第一个Request。
    # 该方法仅仅会被Scrapy调用一次，因此您可以将其实现为生成器。
    def start_requests(self):
        urls = [
            "https://www.zhipin.com/c101040100-p100704/y_5/?query=java&ka=sel-salary-5"
        ]

        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5, 'headers': self.headers, 'cookies': self.cookies},
                                dont_filter=True, splash_headers=self.headers)

    def parse(self, response):
        sel = scrapy.Selector(response)
        links = sel.xpath("//div[@class='primary-box']/@href").extract()
        for link in links:
            url = parse.urljoin("https://www.zhipin.com", link)
            yield SplashRequest(url, self.detail_parse,
                                args={'wait': 0.5, 'headers': self.headers, 'cookies': self.cookies},
                                splash_headers=self.headers)

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
        print("response.url -->", response.url)

        # 职位名称
        job['name'] = response.xpath("//div[@class='info-primary']//h1/text()").extract()[0].strip()
        # 公司名称
        job['co_name'] = response.xpath("//a[@ka='job-detail-company_custompage']/text()").extract()[0]

        # 工资
        job['salary'] = response.xpath("//div[@class='info-primary']//span[@class='salary']/text()").extract()[0]

        # 区域
        job['area'] = response.xpath("//div[@class='info-primary']//p/a/text()").extract()[0]
        job['exp'] = response.xpath("//div[@class='info-primary']//p/text()").extract()[0]
        job['edu'] = response.xpath("//div[@class='info-primary']//p/text()").extract()[1]
        job['otherq'] = ''

        # 福利
        job['welfare'] = ''
        # 职位信息
        posi_info = response.xpath("//div[@class='job-sec']//div[@class='text']/text()").extract()

        job['info'] = '\n'.join(posi_info).strip()
        # 上班地址
        job['local'] = response.xpath("//div[@class='location-address']/text()").extract()[0]

        all_require = response.xpath("//div[@class='sider-company']//p/text()").extract()
        for require in all_require:
            if 'http' in require:
                job['co_url'] = require
            elif '更新于：'.encode("utf-8").decode('utf8') in require:
                job['pub_time'] = require.split('-', 1)[1]

        # 公司行业
        job['co_trade'] = response.xpath('//a[@ka="job-detail-brandindustry"]//text()').extract()[0]
        yield job
