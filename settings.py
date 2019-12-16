import logging
# 默认的配置
LOG_LEVEL = logging.DEBUG    # 默认等级
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
LOG_FILENAME = 'log.log'    # 默认日志文件名称



# 定义代理IP的评分初始值, 方便后期修改
MAX_SCORE = 50


# 检测IP的最大超时等待时间
TEST_TIMEOUT = 10

# mongodb连接地址
MONGO_URL = '127.0.0.1:27017'


# 爬虫任务列表,全目录,全类名/路径
PROXIES_SPIDERS = [
    'core.proxy_spider.proxy_spider.Ip66Spider',
    'core.proxy_spider.proxy_spider.Ip3366Spider',
    'core.proxy_spider.proxy_spider.KuaiSpider',
    'core.proxy_spider.proxy_spider.ProxylistplusSpider',
    'core.proxy_spider.proxy_spider.XiciSpider',
]


# 定时启动爬虫任务时间间隔
SPIDER_TIME_DELAY = 24

# 定时启动检测IP任务时间间隔
TEST_PROXIES_INTERVAL = 12


# 异步检测任务数量
TEST_PROXIES_ASYNC_COUNT = 10

# 配置获取的代理IP最大数量; 这个越小可用性就越高; 但是随机性越差
PROXIES_MAX_COUNT = 50