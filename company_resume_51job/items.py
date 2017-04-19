# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyResume51JobItem(scrapy.Item):
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    position_salary = scrapy.Field()
    position_requirements_label = scrapy.Field()
    position_address = scrapy.Field()
    company_name = scrapy.Field()
    company_label = scrapy.Field()
    company_recruitment_url = scrapy.Field()
    jobs_info = scrapy.Field()
