import scrapy
from ..items import LjItem
import json

class HouseSpider(scrapy.Spider):
    name = 'house'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://www.lianjia.com/city/']

    def parse(self, response):
        # 这里css返回的也是一个生成器列表对象，所以要用get()或getall()方法取出对应的值(data)，只不过get()获得的是第一个对象，返回一个字符串，getall()获取所有对象，返回一个列表
        city_tags = response.css(".city_list_ul a")
        for city_tag in city_tags:
            city_url = city_tag.css("::attr(href)").get()
            city_name = city_tag.css("::text").get()
            item = LjItem(city=city_name)
            # 为了让爬取行政区的时候能够知道来自哪个城市，这里要在yield请求的时候传递一个参数meta，让其携带城市信息
            yield scrapy.Request(city_url + "ershoufang/", callback=self.parse_region_list, meta={"item": item})


    def parse_region_list(self,response):
        region_tags = response.css("div[data-role='ershoufang'] a")
        item = response.meta.get("item")
        for region_tag in region_tags:
            region_url = region_tag.css("::attr(href)").get()
            region_name = region_tag.css("::text").get()
            item['region'] = region_name
            yield scrapy.Request(response.urljoin(region_url), callback=self.parse_page_url, meta={"item": item})

    def parse_page_url(self, response):
        # 翻页
        total_page_str = response.css("div[comp-module='page']::attr(page-data)").get()
        total_page = json.loads(total_page_str)['totalPage']
        for x in range(1, total_page + 1):
            page_url = response.urljoin('pg' + str(x))
            yield scrapy.Request(page_url, callback=self.parse_house_list, meta={"item": response.meta.get('item')})


    def parse_house_list(self, response):
        # 爬取房源的url
        house_url_list = response.css(".sellListContent .title a::attr(href)").getall()
        for house_url in house_url_list:
            yield scrapy.Request(house_url, callback=self.parse_house, meta={"item": response.meta.get('item')})


    def parse_house(self,response):
        item = response.meta.get('item')
        item['title'] = response.css("h1[class='main']::text").get()
        item['total_price'] = response.css(".total::text").get() + '万'
        item['unit_price'] = "".join(response.css(".unitPrice ::text").getall())
        item['house_type'] = response.css(".base .content li:nth-child(1)::text").get()  # css选择器里，空格表示全部，如果想表示直接字结点而不是子孙结点的话可以用>代替空格
        item['orientation'] = response.css(".base .content li:nth-child(7)::text").get()
        item['full_area'] = response.css(".base .content li:nth-child(3)::text").get()
        item['inside_area'] = response.css(".base .content li:nth-child(5)::text").get()
        item['years'] = response.css(".transaction .content li:nth-child(5) span:nth-child(2)::text").get()
        yield item

