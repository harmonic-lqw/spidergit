import datetime
from datetime import timedelta

class ProxyModel(object):
    def __init__(self,proxy_dict):
        # 从请求到并传过来的代理字典中提取出新的代理的url
        proxy = proxy_dict['data'][0]
        # 把代理url绑定到self上
        self.proxy_url = "https://" + proxy['ip'] + ':' + str(proxy['port'])
        # 下面要计算到期时间
        # 获取到期时间
        expire_time_str = proxy['expire_time']
        # 将到期时间的字符串转换成时间     "expire_time":"2019-05-11 22:22:46"}
        self.expire_time = datetime.datetime.strptime(expire_time_str,'%Y-%m-%d %H:%M:%S')
        # 代理是否被加入黑名单标志位,初始设置为False
        self.is_black = False



    # property是个装饰器，能将类方法像属性那样去调用
    @property
    def is_expiring(self):
        # 获取当前时间
        now = datetime.datetime.now()
        # 如果代理过期时间和当前时间对比
        if (self.expire_time - now) <= timedelta(seconds=5):
            return True
        else:
            return False