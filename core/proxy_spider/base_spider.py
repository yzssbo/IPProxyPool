from lxml import etree

from IPProxyPool.domain import Proxy
from IPProxyPool.utils.http import get_request_header
"""
8.3 实现通用爬虫
目标: 实现可以指定不同URL列表, 分组的XPATH和详情的XPATH, 从不同页面上提取代理的IP,端口号和区域的通用爬虫;
步骤:

1. 在base_spider.py文件中,定义一个BaseSpider类, 继承object
2. 提供三个类成员变量:
    urls: 代理IP网址的URL的列表
    group_xpath: 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    detail_xpath: 组内XPATH, 获取代理IP详情的信息XPATH, 格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
3. 提供初始方法, 传入爬虫URL列表, 分组XPATH, 详情(组内)XPATH
4. 对外提供一个获取代理IP的方法
    4.1 遍历URL列表, 获取URL
    4.2 根据发送请求, 获取页面数据
    4.3 解析页面, 提取数据, 封装为Proxy对象
    4.4 返回Proxy对象列表
"""

# 1 在base_spider.py文件中,定义一个BaseSpider类, 继承object
import requests


class BaseSpider(object):
    # 2 提供三个类成员变量:
    # urls : 代理IP网址的URL列表
    urls = []
    # group_xpath: 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    group_xpath = ''
    # detail_xpath: 组内XPATH, 获取代理IP详情的信息XPATH, 格式为:{'ip': 'xx', 'port':'xx', 'area': 'xx'}
    detail_xpath = {}

    web_name = ''

    # 3. 提供初始方法, 传入爬虫URL列表, 分组XPATH, 详情(组内)XPATH
    def __init__(self, urls=[], group_xpath='', detail_xpath={}):
        if urls:
            self.urls = urls

        if group_xpath:
            self.group_xpath = group_xpath

        if detail_xpath:
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        """根据URL 发送请求, 获取页面数据"""
        response = requests.get(url, headers=get_request_header())
        # print(response.content.decode())
        return response.content

    def get_first_from_page(self, lis):
        # 如果列表中有元素就返回第一个, 否则返回空
        return lis[0] if len(lis) != 0 else ''

    def parse_proxies_from_page(self, page, web_name=web_name):
        """解析页面, 提取数据, 封装为Proxy对象"""
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        for tr in trs:
            ip = self.get_first_from_page(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_page(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_page(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area, web_name=web_name)
            yield proxy

    def get_proxies(self):
        # 4. 对外提供一个获取代理IP的方法
        # 4.1 遍历URL列表, 获取URL
        for url in self.urls:
            page = self.get_page_from_url(url)
            proxies = self.parse_proxies_from_page(page)
            # 返回Proxy对象列表
            yield from proxies


if __name__ == '__main__':

    # config = {
    #     'urls': ['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1, 4)],
    #     'group_xpath': '//*[@id="list"]/table/tbody/tr',
    #     'detail_xpath': {
    #         'ip': './td[1]/text()',
    #         'port': './td[2]/text()',
    #         'area': './td[5]/text()'
    #     }
    # }
    config = {
        'urls': ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 4)],
        'group_xpath': '//table[@id="ip_list"]//tr',
        'detail_xpath': {
            'ip': './td[2]/text()',
            'port': './td[3]/text()',
            'area': './td[4]/a/text()'
        }
    }

    spider = BaseSpider(**config)
    count = 0
    for proxy in spider.get_proxies():
        count += 1
        print(proxy)
    print(count)