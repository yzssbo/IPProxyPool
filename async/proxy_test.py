import os
import time
from queue import Queue

import schedule

from IPProxyPool.core.db.mongo_pool import MongoPool
from gevent import monkey

from IPProxyPool.core.proxy_validate.httpbin_validator import check_proxy
from IPProxyPool.settings import TEST_PROXIES_ASYNC_COUNT, MAX_SCORE, TEST_PROXIES_INTERVAL
from max_toolbox.max_logging import MaxLogging

monkey.patch_all()
from gevent.pool import Pool



"""
9. 实现代理池的检测模块
目的: 检查代理IP可用性, 保证代理池中代理IP基本可用
思路
    1. 在proxy_test.py中, 创建ProxyTester类
    2. 提供一个 run 方法, 用于处理检测代理IP核心逻辑
        2.1 从数据库中获取所有代理IP
        2.2 遍历代理IP列表
        2.3 检查代理可用性
        2.4 如果代理不可用, 让代理分数-1, 如果代理分数等于0就从数据库中删除该代理, 否则更新该代理IP
        2.5 如果代理可用, 就恢复该代理的分数, 更新到数据库中
    3. 为了提高检查的速度, 使用异步来执行检测任务
        3.1 在`init`方法, 创建队列和协程池
        3.2 把要检测的代理IP, 放到队列中
        3.3 把检查一个代理可用性的代码, 抽取到一个方法中; 从队列中获取代理IP, 进行检查; 检查完毕, 调度队列的task_done方法
        3.4 通过异步回调, 使用死循环不断执行这个方法,
        3.5 开启多个一个异步任务, 来处理代理IP的检测; 可以通过配置文件指定异步数量
   4. 使用schedule模块, 每隔一定的时间, 执行一次检测任务
        4.1 定义类方法 start, 用于启动检测模块
        4.2 在start方法中
            4.2.1 创建本类对象
            4.2.2 调用run方法
            4.2.3 每间隔一定时间, 执行一下, run方法  
"""

log_name = 'ProxyTest'
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs', 'proxy_test.log')
MaxLogging.init(log_file, log_name)


class ProxyTester(object):
    def __init__(self):
        # 创建操作数据库的MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1 在'init' 方法中创建队列和协程池
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_callback(self, temp):
        self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

    def run(self):
        # 提供一个 run 方法, 用于处理检测代理IP的核心逻辑
        # 2.1 从数据库中获取所有代理IP
        proxies = self.mongo_pool.find_all()
        # 2.2 遍历代理Ip列表
        for proxy in proxies:
            # 3.2 把要检测的代理IP, 放入队列
            self.queue.put(proxy)

        # 3.5 开启多个异步任务,  来处理代理IP的检测, 可以通过配置文件控制异步任务数量
        for i in range(TEST_PROXIES_ASYNC_COUNT):
            # 3.4 通过异步回调, 使用死循环不断执行这个方法
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        # 让当前线程 等待队列中所有任务完成
        self.queue.join()

    def __check_one_proxy(self):
        # 检查一个代理IP的可用性
        # 3.3从队列中获取代理IP, 进行检查
        proxy = self.queue.get()
        # 2.3 检查代理可用性
        proxy = check_proxy(proxy)
        # 2.4 如果代理不可用, 让代理分数-1
        if proxy.speed == -1:
            proxy.score -= 1
            # 如果代理分数等于0就从数据库中删除该代理IP
            if proxy.score == 0:
                self.mongo_pool.delete_one(proxy)
                MaxLogging.get_logger(log_name).info('del useless ip {}'.format(proxy.ip))
            else:
                # 否则更新该代理IP分数
                self.mongo_pool.update_one(proxy)
                MaxLogging.get_logger(log_name).info('ip {0} score decrement {1}'.format(proxy.ip, proxy.score))

        else:
            # 如果代理IP可用, 并且此时分数不为满分时, 就恢复该代理的分数,并更新
            if proxy.score != MAX_SCORE:
                proxy.score = MAX_SCORE
            self.mongo_pool.update_one(proxy)
            MaxLogging.get_logger(log_name).info('update ip score {}'.format(proxy.ip))

        # 调度队列的task_done方法, 通知队列当前单位任务已完成
        self.queue.task_done()

    @classmethod
    def start(cls):

        #  4.2.1 调用run方法
        cls().run()


if __name__ == '__main__':
    ProxyTester.start()
    # 4.2.2 每间隔一定时间, 执行一下, run方法
    schedule.every(TEST_PROXIES_INTERVAL).hours.do(ProxyTester.start)
    stop_file = os.path.join(os.path.dirname(__file__), '__stop_proxy_test__')
    while True:
        if os.path.exists(stop_file):
            break
        schedule.run_pending()
        time.sleep(1)
