# 打猴子补丁
import os

from gevent import monkey

from max_toolbox.max_logging import MaxLogging

monkey.patch_all()
# 导入协程池
from gevent.pool import Pool

import schedule
import time
import importlib

from IPProxyPool.core.db.mongo_pool import MongoPool
from IPProxyPool.core.proxy_validate.httpbin_validator import check_proxy
from IPProxyPool.settings import PROXIES_SPIDERS, SPIDER_TIME_DELAY

"""
8.5 实现运行爬虫模块
目标: 根据配置文件信息, 加载爬虫, 抓取代理IP, 进行校验, 如果可用, 写入到数据库中
思路:

1. 在run_spider.py中, 创建RunSpider类
2. 提供一个运行爬虫的run方法, 作为运行爬虫的入口, 实现核心的处理逻辑
    2.1 根据配置文件信息, 获取爬虫对象列表.
    2.2 遍历爬虫对象列表, 获取爬虫对象, 遍历爬虫对象的get_proxies方法, 获取代理IP
    2.3 检测代理IP(代理IP检测模块)
    2.4 如果可用,写入数据库(数据库模块)
    2.5 处理异常, 防止一个爬虫内部出错了, 影响其他的爬虫.
3. 使用异步来执行每一个爬虫任务, 以提高抓取代理IP效率
    3.1 在init方法中创建协程池对象
    3.2 把处理一个代理爬虫的代码抽到一个方法
    3.3 使用异步执行这个方法
    3.4 调用协程的join方法, 让当前线程等待 协程 任务的完成.
4. 使用schedule模块, 实现每隔一定的时间, 执行一次爬取任务
    4.1 定义一个start的类方法
    4.2 创建当前类的对象, 调用run方法
    4.3 使用schedule模块, 每隔一定的时间, 执行当前对象的run方法
"""
log_name = 'RunSpider'
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs', 'run_spider.log')
MaxLogging.init(log_file, log_name)


class RunSpider(object):
    def __init__(self):
        # 创建MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1 在init方法中创建协程池对象
        self.coroutine_pool = Pool()

    def get_spider_from_settings(self):
        """根据胚子文件信息, 获取爬虫对象列表"""
        # 首先遍历配置文件中的爬虫信息, 获取每个爬虫全类名
        for full_class_name in PROXIES_SPIDERS:
            # core.proxy_spider.proxy_spiders.Ip66Spider
            # 获取模块名和类名,然后根据模块名动态创建类对象
            module_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            print(module_name)
            print(class_name)
            # 根据模块名导入模块
            module = importlib.import_module(module_name)
            # 根据模块获取爬虫对象
            cls = getattr(module, class_name)
            # 创建爬虫对象
            spider = cls()
            yield spider

    def run(self):
        # 2.1 根据配置文件信息,获取爬虫对象列表
        spiders = self.get_spider_from_settings()
        for spider in spiders:
            # 2.2 遍历爬虫对象列表, 获取爬虫对象, 遍历爬虫对象的get_proxies方法, 获取代理IP
            # self._execute_one_spider_task(spiders)
            # 抽取出的方法使用线程池调度
            print(spider)
            self.coroutine_pool.apply_async(self._execute_one_spider_task, args=(spider, ))
        # 3.4 调用协程的 join方法, 让当前线程等待协程任务的完成
        self.coroutine_pool.join()

    def _execute_one_spider_task(self, spider):
        try:
            # 遍历爬虫对象的get_proxies方法, 获取代理IP
            for proxy in spider.get_proxies():
                # 2.3 检测代理IP(代理IP检测模块)
                proxy = check_proxy(proxy)
                # 如果速度不为-1, 说明可用
                if proxy.speed != -1:
                    # 写入数据库
                    self.mongo_pool.insert_one(proxy)
        except Exception as e:
            MaxLogging.get_logger(log_name).exception(e)

    @classmethod
    def start(cls):
        cls().run()


if __name__ == '__main__':
    RunSpider.start()
    schedule.every(SPIDER_TIME_DELAY).hours.do(RunSpider.start)
    stop_file = os.path.join(os.path.dirname(__file__), '__stop_run_spider__')
    while True:
        if os.path.exists(stop_file):
            break
        schedule.run_pending()
        time.sleep(1)
