# -*- coding: utf-8 -*-

import scrapy


class Job51Item(scrapy.Item):
    name = scrapy.Field()
    co_name = scrapy.Field()
    area = scrapy.Field()
    salary = scrapy.Field()
    exp = scrapy.Field()
    edu = scrapy.Field()
    num = scrapy.Field()
    time = scrapy.Field()
    otherq = scrapy.Field()
    welfare = scrapy.Field()
    info = scrapy.Field()
    local = scrapy.Field()
    co_url = scrapy.Field()
    co_type = scrapy.Field()
