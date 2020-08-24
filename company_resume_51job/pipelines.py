# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
from elasticsearch import Elasticsearch, helpers

settings = get_project_settings()


class CompanyResume51JobPipeline(object):
    def __init__(self):
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        db_name = settings['MONGODB_DBNAME']
        client = MongoClient(host=host, port=port)
        db = client[db_name]
        self.post = db[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        job_info = dict(item)
        self.post.insert(job_info)
        return item


class EsPipeline(object):
    def __init__(self):
        host = settings['ES_HOST']
        port = settings['ES_PORT']
        self.client = Elasticsearch([{"host": host, "port": port, "timeout": 1500}])

    def process_item(self, item, spider):
        job_info = dict(item)
        db = settings['ES_INDEX']
        table = settings['ES_TYPE']

        bulks = [{
            "_index": db,
            # "_type": table,
            "_source": job_info
        }]

        helpers.bulk(self.client, bulks)
        return item


def start_redis(website):
    redis_q = redis.StrictRedis(
        connection_pool=redis.ConnectionPool(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'], db=0))

    redis_key = '{}:start_urls'.format(website)
    start_urls = 'https://www.{}.com'.format(website)
    redis_q.lpush(redis_key, start_urls)
    redis_q.close()
