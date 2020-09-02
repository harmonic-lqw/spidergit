# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from twisted.enterprise import adbapi

class LywPipeline:
    def __init__(self,mysql_confige):
        self.dbpool = adbapi.ConnectionPool(
            mysql_confige['DRIVER'],
            host=mysql_confige['HOST'],
            port=mysql_confige['PORT'],
            user=mysql_confige['USER'],
            password=mysql_confige['PASSWORD'],
            db=mysql_confige['DATABASE'],
            charset="utf8"
        )

    @classmethod
    #只要重写了from_crawler方法，那么以后创建对象的时候，就会调用这个方法来获取pipline对象
    def from_crawler(cls,crawler):
        mysql_cofige = crawler.settings['MYSQL_CONFIGE']
        return cls(mysql_cofige)


    def process_item(self, item, spider):
        result = self.dbpool.runInteraction(self.insert_item,item)
        result.addErrback(self.insert_error)
        return item

    def insert_item(self,cursor,item):
        sql = "insert into artical(id,title,pub_time,author,content,origin) value(null,%s,%s,%s,%s,%s)"
        args = (item['title'],item['pub_time'],item['author'],item['content'],item['origin'])
        cursor.execute(sql,args)

    def insert_error(self,failure):
        print("="*30)
        print(failure)
        print("="*30)

    def cose_spider(self):
        self.dbpool.close()



