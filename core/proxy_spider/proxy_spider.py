import random
import time

from IPProxyPool.core.proxy_spider.base_spider import BaseSpider



"""
1. 实现西刺代理爬虫: http://www.xicidaili.com/nn/1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""

class XiciSpider(BaseSpider):
    # 准备URl列表
    urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 7)]

    # 分组内的xpath
    group_xpath = '//table[@id="ip_list"]//tr[position()>1]'

    # 组内的xpath, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[4]/a/text()'
    }

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)


"""
2. 实现ip3366代理爬虫: http://www.ip3366.net/free/?stype=1&page=1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""

class Ip3366Spider(BaseSpider):
    # 准备URl列表
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for i in range(1, 4, 2) for j in range(1, 8)]

    # 分组内的xpath
    group_xpath = '//*[@id="list"]/table/tbody/tr'

    # 组内的xpath, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()'
    }
    web_name = 'ip3366'

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)

    def parse_proxies_from_page(self, page, web_name=web_name):
        return super().parse_proxies_from_page(page, web_name)


"""
3. 实现快代理爬虫: https://www.kuaidaili.com/free/inha/1/
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""
class KuaiSpider(BaseSpider):
    # 准备URl列表
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 6)]

    # 分组内的xpath
    group_xpath = '//*[@id="list"]/table/tbody/tr'

    # 组内的xpath, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()'
    }

    web_name = 'kuaidaili'

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)

    def parse_proxies_from_page(self, page, web_name=web_name):
        return super().parse_proxies_from_page(page, web_name)


"""
4. 实现proxylistplus代理爬虫: https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""
class ProxylistplusSpider(BaseSpider):
    # 准备URl列表
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]

    # 分组内的xpath
    group_xpath = '//*[@id="page"]/table[2]//tr[position()>2]'

    # 组内的xpath, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[5]/text()'
    }
    web_name = 'proxylist'

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)

    def parse_proxies_from_page(self, page, web_name=web_name):
        return super().parse_proxies_from_page(page, web_name)


"""
5. 实现66ip爬虫: http://www.66ip.cn/1.html
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
    由于66ip网页进行js + cookie反爬, 需要重写父类的get_page_from_url方法
    后来这个反扒他又取消了
"""
class Ip66Spider(BaseSpider):
    # 准备URL列表
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 6)]
    urls.extend(['http://www.66ip.cn/areaindex_{0}/{1}.html'.format(i, j) for i in range(1, 10) for j in range(1, 10)])
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="main"]/div[1]/div[2]/div[1]/table/tbody/tr[position()>1]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[3]/text()'
    }

    web_name = 'ip66'

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)

    def parse_proxies_from_page(self, page, web_name=web_name):
        return super().parse_proxies_from_page(page, web_name)


if __name__ == '__main__':
    # spider = XiciSpider()
    # spider = Ip3366Spider()
    # spider = KuaiSpider()
    # spider = ProxylistplusSpider()
    spider = Ip66Spider()
    count = 0
    # for proxy in spider.get_proxies():
    #     count += 1
    #     print(proxy)
    for ip in spider.urls:
        print(ip)
        count += 1
    print(count)
