from scrapy import cmdline
from company_resume_51job.pipelines import start_redis

# website = 'zhipin'
website = '51job'
# website = 'lagou'
# website = 'zhilian'
# website = 'liepin'
# start_redis(website)
cmdline.execute("scrapy crawl {}".format(website).split())
