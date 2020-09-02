# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
from .models import ProxyModel
import threading
import time

# # # # # # # 更换代理的时候最好用多线程，以为异步更换代理，内部逻辑比较复杂，可以用多线程来进行代理更换控制


class IPDownloaderMiddleware(object):
    def __init__(self):
        super(LiepinDownloaderMiddleware, self).__init__()
        self.current_proxy = None
        # 从代理商获得的代理的url
        self.update_proxy_url = ""
        # 请求代理url时的请求头
        self.headers = {

        }
        # 执行更新代理
        self.update_proxy()
        # 因为后面对self.current_proxy.is_blacked有改变，所以在改变的时候要用到锁
        self.Lock = threading.Lock()
        # 此时用多线程来管理代理IP的更换
        th = threading.Thread(target=self.update_proxy_in_thread())
        th.start()



    def process_request(self, request, spider):
        # 发送请求之前更新代理
        request.meta['proxy'] = self.current_proxy.proxy_url
        return None

    def process_response(self, request, response, spider):
        # 在响应中，通过判断状态码，来判断是否更新代理
        if response.status != 200:
            # 开启锁
            self.Lock.acquire()
            # 将代理过期的标志位变成Ture，标记这个代理已经过期
            self.current_proxy.is_blacked = True
            # 关闭锁
            self.Lock.release()
            # 这个时候要讲请求重新发送
            return request
        # 如果没过期，则返回response，继续执行之后的process_response
        return response

    def update_proxy(self):
        # 请求从代理商获得的代理url
        resp = requests.get(self.update_proxy_url,headers=self.headers)
        # 获得代理模型
        proxy_model = ProxyModel(resp.json())
        self.current_proxy = proxy_model

    def update_proxy_in_thread(self):
        # 定义的管理方式为一分钟更换一次代理（这里可以根据所要爬取网站的反爬强度，以及setting中设置的爬取时间间隔来综合考虑）
        # 为了颗粒化计数
        count = 0
        while True:
            time.sleep(10)
            if count >= 60 or self.current_proxy.is_blacked:
                self.update_proxy()
                count = 0
                print("此时更新了代理，代理为：%s"%self.current_proxy.proxy_url)
            else:
                count += 1

