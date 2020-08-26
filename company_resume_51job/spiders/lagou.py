import os
import time
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy_splash import SplashRequest
from company_resume_51job.items import Job51Item


class JobSpider(RedisSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']

    def start_requests(self):
        urls = [
            "https://www.lagou.com/jobs/list_java?px=new&yx=15k-25k&city=%E9%87%8D%E5%BA%86#order",
            "https://www.lagou.com/jobs/list_技术总监?px=new&yx=15k-25k&city=%E9%87%8D%E5%BA%86#order",
            "https://www.lagou.com/jobs/list_架构师?px=new&yx=15k-25k&city=%E9%87%8D%E5%BA%86#order",
        ]

        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5}, dont_filter=True)

    def parse(self, response):
        sel = scrapy.Selector(response)
        links = sel.xpath("//div[@class='s_position_list ']//a[@class='position_link']/@href").extract()
        for link in links:
            yield scrapy.Request(url=link, callback=self.detail_parse, priority=1)

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
        repo = response.xpath('//div[@class="position-content-l"]//h1//text()').extract()
        # if len(repo) <= 0:
        #     print("报错了")
        #     return

        job['name'] = response.xpath('//div[@class="position-content-l"]//h1//text()').extract()[0].strip()
        # 公司名称
        job['co_name'] = response.xpath('//div[@class="job_company_content"]//em[@class="fl-cn"]//text()').extract()[0].strip()

        resp = response.xpath('//dd[@class="job_request"]//h3/span//text()').extract()
        # 工资
        job['salary'] = resp[0].strip()
        # 区域
        job['area'] = resp[1].strip("/").strip()
        job['exp'] = resp[2].strip("/").strip().strip("经验")
        job['edu'] = resp[3].strip("/").strip()
        job['otherq'] = response.xpath('//p[@class="publish_time"]//text()').extract()[0]

        # 福利
        job['welfare'] = response.xpath('//dd[@class="job-advantage"]//p//text()').extract()[0]
        # 职位信息
        posi_info = response.xpath('//div[@class="job-detail"]//text()').extract()

        job['info'] = '\n'.join(posi_info).strip()
        # 上班地址
        local = response.xpath('//div[@class="work_addr"]/a//text()').extract()
        if len(local) > 0:
            job['local'] = ''.join(local).strip("查看地图")
        # 公司网址
        job['co_url'] = response.xpath('//h4[@class="c_feature_name"]//text()').extract()[3]
        # 公司行业
        job['co_trade'] = response.xpath('//h4[@class="c_feature_name"]//text()').extract()[0]
        yield job
