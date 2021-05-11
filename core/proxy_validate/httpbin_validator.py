"""
 实现代理池的校验模块
目标: 检查代理IP速度,匿名程度以及支持的协议类型.
步骤:

检查代理IP速度 和 匿名程度;
    1. 代理IP速度: 就是从发送请求到获取响应的时间间隔
    2. 匿名程度检查:
        1. 对 http://httpbin.org/get 或 https://httpbin.org/get 发送请求
        2. 如果 响应的origin 中有','分割的两个IP就是透明代理IP
        3. 如果 响应的headers 中包含 Proxy-Connection 说明是匿名代理IP
        4. 否则就是高匿代理IP
检查代理IP协议类型
    如果 http://httpbin.org/get 发送请求可以成功, 说明支持http协议
    如果 https://httpbin.org/get 发送请求可以成功, 说明支持https协议
"""



import json
import time

import requests

from IPProxyPool.domain import Proxy
from IPProxyPool.settings import TEST_TIMEOUT
from IPProxyPool.utils import http


# 内部封装一个私有方法:检测方法
# 默认的是检测http的,若需要检测https需要传入false
def __check_http_proxies(proxies, is_http=True):
    # 匿名类型: 高匿:0, 匿名:1, 透明:2
    nick_type = -1
    # 响应速度, 单位s
    speed = -1

    if is_http:
        test_url = 'http://httpbin.org/get'
    else:
        test_url = 'https://httpbin.org/get'

    try:
        # 获取访问开始时间
        start_time = time.time()
        response = requests.get(test_url, headers=http.get_request_header(), timeout=TEST_TIMEOUT, proxies=proxies)

        if response.ok:
            # 计算响应速度
            speed = round(time.time() - start_time, 2)
            # 将响应的json字符转转换成字典
            dict = json.loads(response.content)
            # 获取来源IP: origin
            origin = dict['origin']
            proxy_connection = dict['headers'].get('Proxy_Connection', None)
            if ',' in origin:
                # 1.如果响应的origin中包含',' 分割的两个IP,说明该代理IP为透明IP
                nick_type = 2
            elif proxy_connection:
                # 2.如果响应的headers中包含 Proxy_Connection 说明是匿名代理IP
                nick_type = 1
            else:
                # 3.否则既不包含',' 也不包含 Proxy_Connection则说明为高匿代理IP
                nick_type = 0
            return True, nick_type, speed
        return False, nick_type, speed
    except Exception as e:
        # 代理IP不稳定不能用的太多了,这里就不必要记录太多没有用的错误日志
        # logger.error(e)
        return False, nick_type, speed


# 对外提供一个检测接口, 需要接收一个代理ip参数
def check_proxy(proxy):
    """
      用于检查指定 代理IP 响应速度, 匿名程度, 支持协议类型
      :param proxy: 代理IP模型对象
      :return: 检查后的代理IP模型对象
    """

    # 准备代理IP字典
    proxies = {
        'http': 'http://{}:{}'.format(proxy.ip, proxy.port),
        'https': 'https://{}:{}'.format(proxy.ip, proxy.port)
    }

    # 测试该代理IP
    http, http_nick_type, http_speed = __check_http_proxies(proxies)
    https, https_nick_type, https_speed = __check_http_proxies(proxies, False)
    # 代理IP支持的协议类型, http是0, https是1, https和http都支持是2
    if http and https:
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = https_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    return proxy


if __name__ == '__main__':
    proxy = Proxy('60.176.234.179', port='8888')

    # proxy = Proxy('114.239.148.160', port='808')
    # proxy = Proxy('117.69.200.125', port='31627')
    print(check_proxy(proxy))