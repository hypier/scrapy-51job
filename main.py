from scrapy import cmdline
from company_resume_51job.pipelines import start_redis

website = '51job'
start_redis(website)
cmdline.execute("scrapy crawl {}".format(website).split())
