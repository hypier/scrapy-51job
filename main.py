from scrapy import cmdline
from company_resume_51job.pipelines import start_redis

# start_redis('51job')
start_redis('liepin')
cmdline.execute("scrapy crawl 51job".split())
