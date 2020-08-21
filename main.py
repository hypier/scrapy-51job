import redis
from scrapy import cmdline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
redis_q = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'], db=0))

redis_key = 'liepin:start_urls'
start_urls = 'http://www.liepin.com'
redis_q.lpush(redis_key, start_urls)
redis_q.close()
cmdline.execute("scrapy crawl liepin".split())
