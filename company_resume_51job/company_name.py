#!/use/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
import requests
import urllib.parse
import redis

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

redis_q = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))


def PositionUrl(Html):
    selector = html.fromstring(Html)
    position = selector.xpath('//div[@id="resultList"]/div[@class="el"]')
    for i in position:
        url = i.xpath('p/span/a/@href')[0]
        redis_q.lpush('51job:start_urls', url)


print("Please according to the prompt to input, must strictly careful operation in order to avoid waste your how many repair operations.")
print("Please enter 'http://www.51job.com/' website for company name to crawl, must be the full name, it doesn't matter too much or you will climb to the company requirements.")
Company_name = urllib.parse.quote(input("Please enter the need to search the company name: "))
Pages = 1

urls = 'http://search.51job.com/list/000000,000000,0000,00,9,99,{0},2,{1}.html'.format(Company_name, Pages)

Request = requests.get(url=urls).content
PositionUrl(Request)

selector = html.fromstring(Request)

NumberPages = selector.xpath('//div[@class="dw_table"]/div[@class="dw_tlc"]/div[@class="rt"]/text()')[2].split('/ ')[1]

for i in range(2, int(NumberPages)+1):
    urls = 'http://search.51job.com/list/000000,000000,0000,00,9,99,{0},2,{1}.html'.format(Company_name, i)
    print(urls)
    Request = requests.get(url=urls).content
    PositionUrl(Request)

print("执行完毕请查看 Redis 队列信息.")