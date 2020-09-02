import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import LywItem

class LywSpiderSpider(CrawlSpider):
    name = 'lyw_spider'
    allowed_domains = ['lieyunwang.com']
    start_urls = ['https://www.lieyunwang.com/latest/p1.html']

    rules = (
        Rule(LinkExtractor(allow=r'/latest/p\d+\.html'), follow=True),
        Rule(LinkExtractor(allow=r'/archives/\d+'), callback='parse_detail', follow=False),
    )

    def parse_detail(self, response):
        title = "".join(response.xpath("//h1[@class = 'lyw-article-title-inner']/text()").getall()).strip()
        pub_time = response.xpath("//h1[@class = 'lyw-article-title-inner']/span/text()").get()
        author = response.xpath("//a[@class = 'author-name open_reporter_box']/text()").get()
        content = "".join(response.xpath("//div[@id = 'main-text-id']//text()").getall())
        origin = response.url
        item = LywItem(title=title,pub_time=pub_time,author=author,content=content,origin=origin)
        return item

