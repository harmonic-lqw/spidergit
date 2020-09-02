# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LiepinItem(scrapy.Item):
    title = scrapy.Field()
    salary = scrapy.Field()
    edu = scrapy.Field()
    experience = scrapy.Field()
    work_need = scrapy.Field()
