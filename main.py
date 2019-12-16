from multiprocessing import Process

from core.proxy_api import ProxyApi
from core.proxy_spider.run_spider import RunSpider
from core.proxy_test import ProxyTester


def run():
    # 1 定义一个列表,用于存储需要启动的进程
    process_list = []
    # 2 创建 启动爬虫 的进程, 添加列表
    process_list.append(Process(target=RunSpider.start))
    # 3 创建 启动检测 的进程, 添加到列表
    process_list.append(Process(target=ProxyTester.start))
    # 4 创建 启动FLask API接口 的进程, 添加进列表
    process_list.append(Process(target=ProxyApi.start))

    for process in process_list:
        # 5 守护进程
        process.daemon = True
        process.start()

    # 6 遍历进程列表, 让主进程等待子进程的完成
    for process in process_list:
        process.join()


if __name__ == '__main__':
    run()