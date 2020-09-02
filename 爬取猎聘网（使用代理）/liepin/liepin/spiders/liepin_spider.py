import scrapy
from scrapy.spiders.crawl import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import LiepinItem

class LiepinSpiderSpider(CrawlSpider):
    name = 'liepin_spider'
    allowed_domains = ['liepin.com']
    start_urls = ['https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key=python']
    # rules中最后一个Rule要有逗号

    rules = (
        Rule(LinkExtractor(allow=r"https://www.liepin.com/job/\d+\.shtml.*", restrict_xpaths=['//ul[@class="sojob-list"]//a']), callback="parse_job", follow=False),
        # Rule(LinkExtractor(allow=r"zhaopin/.+?curPage=\d+",restrict_xpaths=["//div[@class='pager']//a"]),follow=True)

    )

    def parse_job(self, response):
        title = response.css(".title-info h1::text").get()
        salary = response.css(".job-title-left p::text").get().strip()
        edu = response.css(".job-qualifications span:nth-child(1) ::text").get()
        experience =  response.css(".job-qualifications span:nth-child(2) ::text").get()
        work_need_list = response.css(".content-word::text").getall()
        work_need = "".join(work_need_list).strip()
        item = LiepinItem(title=title,salary=salary,edu=edu,experience=experience,work_need=work_need)
        yield item



