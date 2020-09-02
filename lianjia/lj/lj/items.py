# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LjItem(scrapy.Item):
    # 标题
    title = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 行政区
    region = scrapy.Field()
    # 总价
    total_price = scrapy.Field()
    # 单价
    unit_price = scrapy.Field()
    # 户型
    house_type = scrapy.Field()
    # 朝向
    orientation = scrapy.Field()
    # 总面积
    full_area = scrapy.Field()
    # 套内面积
    inside_area = scrapy.Field()
    # 年份
    years = scrapy.Field()

