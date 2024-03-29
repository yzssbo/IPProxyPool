import os
import random

import pymongo
from pymongo import MongoClient

from IPProxyPool.domain import Proxy
from IPProxyPool.settings import MONGO_URL
from max_toolbox.max_logging import MaxLogging

"""
7. 实现代理池的数据库模块
作用: 用于对proxies集合进行数据库的相关操作
目标: 实现对数据库增删改查相关操作
步骤:
1. 在init中, 建立数据连接, 获取要操作的集合, 在 del 方法中关闭数据库连接

2.提供基础的增删改查功能
    2.1 实现插入功能
    2.2 实现修改该功能
    2.3 实现删除代理: 根据代理的IP删除代理
    2.4 查询所有代理IP的功能
3. 提供代理API模块使用的功能
    3.1 实现查询功能: 根据条件进行查询, 可以指定查询数量, 先分数降序, 速度升序排, 保证优质的代理IP在上面.
    3.2 实现根据协议类型 和 要访问网站的域名, 获取代理IP列表
    3.3 实现根据协议类型 和 要访问网站的域名, 随机获取一个代理IP
    3.4 实现把指定域名添加到指定IP的disable_domain列表中.
"""
log_name = 'MongoPoolLog'
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../logs', 'mongo_pool.log')
MaxLogging.init(log_file, log_name)


class MongoPool(object):
    def __init__(self):
        # 1.1 在init中, 建立数据库的链接
        self.client = MongoClient(MONGO_URL)
        # 1.2 获取要操作的集合
        self.db = self.client['admin']
        self.db.authenticate('yzssbo', 'yy961124')

        self.proxies = self.client['proxies_pool']['proxies']

    def __del__(self):
        # 1.3 关闭数据库连接
        self.client.close()

    def insert_one(self, proxy):
        """2.1 实现插入功能"""
        count = self.proxies.count_documents({'_id': proxy.ip})
        if count == 0:
            dict = proxy.__dict__

            dict['_id'] = proxy.ip
            self.proxies.insert_one(dict)
            MaxLogging.get_logger(log_name).warning('已插入代理IP:{}'.format(proxy))
        else:
            MaxLogging.get_logger(log_name).warning('已存在代理IP:{}'.format(proxy))

    def update_one(self, proxy):
        """2.2 实现修改功能"""
        self.proxies.update_one({'_id': proxy.ip}, {'$set': proxy.__dict__})

    def delete_one(self, proxy):
        """2.3 实现删除代理: 根据代理的Ip进行删除"""
        self.proxies.delete_one({'_id': proxy.ip})
        MaxLogging.get_logger(log_name).info('删除代理IP:{}'.format(proxy))

    def find_all(self):
        """2.4 查找所有代理IP"""
        # 查找到的是所有IP的字典集合
        cursor = self.proxies.find()
        for item in cursor:
            # 为了生成proxy对象返回,所以需要删除冗余的_id字段
            item.pop('_id')
            # print(**item)
            proxy = Proxy(**item)
            yield proxy

    def find(self, conditions={}, count=0):
        """
        3.1 实现查询功能: 根据条件进行查询, 可以指定查询数量, 先分数降序, 速度升序排, 保证优质的代理IP在上面.
        :param conditions: 查询条件字典
        :param count: 限制最多取出多少个代理IP
        :return: 返回满足要求代理IP(Proxy对象)列表
        """
        try:
            cursor = self.proxies.find(conditions, limit=count).sort(
                [('score', pymongo.DESCENDING), ('speed', pymongo.ASCENDING)]
            )
        except Exception as e:
            MaxLogging.get_logger(log_name).error(e)


        # 准备列表  用于存储查询处理代理IP
        proxy_list = []
        # 遍历cursor
        for item in cursor:
            item.pop('_id')
            proxy = Proxy(**item)
            proxy_list.append(proxy)

        return proxy_list

    def get_proxies(self, protocol=None, domain=None, count=0, nick_type=2):
        """
        3.2 实现根据协议类型 和 要访问网站的域名, 获取代理IP列表
        :param protocol: 协议: http, https
        :param domain: 域名: jd.com
        :param count:  用于限制获取多个代理IP, 默认是获取所有的
        :param nick_type: 匿名类型, 默认, 获取高匿的代理IP
        :return: 满足要求代理IP的列表
        """
        # 定义查询条件
        conditions = {'nick_type': nick_type}
        # 根据协议, 指定查询条件
        if protocol is None:
            # 如果没有传入协议类型, 返回既支持http也支持https的代理IP
            conditions['protocol'] = 2
        elif protocol.lower() == 'http':
            conditions['protocol'] = {'$in': [0, 2]}
        else:
            conditions['protocol'] = {'$in': [1, 2]}

        if domain:
            # 如果指定了要访问的域名, 那么代理IP中的不可用域名中不能包含该域名
            conditions['disable_domains'] = {'$nin': [domain]}

        # 根据条件筛选出满足条件的代理IP列表
        return self.find(conditions, count=count)

    def random_proxy(self, protocol=None, domain=None, count=0, nick_type=2):
        """
        3.3 实现根据协议类型 和 要访问网站的域名, 随机获取一个代理IP
        :param protocol: 协议: http, https
        :param domain: 域名: jd.com
        :param count:  用于限制获取多个代理IP, 默认是获取所有的
        :param nick_type: 匿名类型, 默认, 获取高匿的代理IP
        :return: 满足要求的随机的一个代理IP(Proxy对象)
        """
        proxy_list = self.get_proxies(protocol=protocol, domain=domain, count=count, nick_type=nick_type)
        # 从proxy_list列表中随机获取一个IP代理返回
        return random.choice(proxy_list)

    def disable_domain(self, ip, domain):
        """
        3.4 实现把指定域名添加到指定IP的disable_domain列表中.
        :param ip: IP地址
        :param domain: 域名
        :return: 如果返回True, 就表示添加成功了, 返回False添加失败了
        """
        ip_count = self.proxies.count_documents({'_id': ip})
        count = self.proxies.count_documents({'_id': ip, 'disable_domains': domain})
        if count == 0 and ip_count == 0:
            # 如果disable_domains字段中没有这个域名,再去添加
            self.proxies.update_one({'_id': ip}, {'$push': {'disable_domains': domain}})
            return True
        return False


if __name__ == '__main__':
    mongo = MongoPool()
    # proxy = Proxy('192.168.0.1', port='1288')
    # # a.insert_one(proxy)
    # # proxy1 = Proxy('60.176.234.172', port='9999')
    # # a.update_one(proxy1)
    # a.delete_one(proxy)

    # for proxy in a.find_all():
    #
    #     print(proxy)

    # dic = { "ip" : "202.104.113.38", "port" : "53281", "protocol" : 0, "nick_type" : 0, "speed" : 8.2, "area" : None, "score" : 50, "disable_domains" : [ "jd.com"] }
    # dic = { "ip" : "202.104.113.39", "port" : "53281", "protocol" : 1, "nick_type" : 0, "speed" : 1.2, "area" : None, "score" : 50, "disable_domains" : [ "taobao.com"] }
    # dic = { "ip" : "202.104.113.40", "port" : "53281", "protocol" : 2, "nick_type" : 0, "speed" : 4.0, "area" : None, "score" : 50, "disable_domains" : []}
    # dic = { "ip" : "202.104.113.41", "port" : "53281", "protocol" : 2, "nick_type" : 0, "speed" : -1, "area" : None, "score" : 49, "disable_domains" : []}
    # proxy = Proxy(**dic)
    # mongo.insert_one(proxy)
    # for proxy in mongo.get_proxies(protocol='https'):
    #     print(proxy)
    proxies = mongo.random_proxy(count=0)
    for i in proxies:
        print(i)

    # print(mongo.disable_domain('202.104.113.38', 'taobao.com'))

