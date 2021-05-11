import json
import os

from flask import Flask, request

from IPProxyPool.core.db.mongo_pool import MongoPool
from IPProxyPool.settings import PROXIES_MAX_COUNT
from max_toolbox.max_logging import MaxLogging


log_name = 'App'
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs', 'app.log')
MaxLogging.init(log_file, log_name)


class ProxyApi(object):
    def __init__(self):
        # 2.1 初始化一个Flask的Web服务
        self.app = Flask(__name__)
        # 创建mongodb数据库连接对象
        self.mongo_pool = MongoPool()
        self.app.logger = MaxLogging.get_logger(log_name)

        @self.app.route('/random')
        def random():
            """
            2.2 实现根据协议类型和域名, 提供随机的获取高可用代理IP的服务
                可用通过 protocol 和 domain 参数对IP进行过滤
                protocol: 当前请求的协议类型
                domain: 当前请求域名
            """
            protocol = request.args.get('protocol')
            domain = request.args.get('domain')
            nick_type = request.args.get('nick_type')
            try:
                proxy = self.mongo_pool.random_proxy(protocol=protocol, domain=domain, nick_type=int(nick_type), count=PROXIES_MAX_COUNT)
            except Exception as e:
                self.app.logger.exception(e)
                return '数据库无法获取对应的Ip,请更改参数后重试'
            if protocol:
                return '{}://{}:{}'.format(protocol, proxy.ip, proxy.port)
            else:
                return '{}:{}'.format(proxy.ip, proxy.port)

        @self.app.route('/proxies')
        def proxies():
            """
               2.3 实现根据协议类型和域名, 提供获取多个高可用代理IP的服务
               可用通过protocol 和 domain 参数对IP进行过滤
               实现给指定的IP上追加不可用域名的服务
            """
            # 获取协议: http/ https
            protocol = request.args.get('protocol')
            # 域名: 如 jd.com
            domain = request.args.get('domain')
            nick_type = request.args.get('nick_type')
            try:
                proxies = self.mongo_pool.get_proxies(protocol=protocol, domain=domain, nick_type=int(nick_type), count=PROXIES_MAX_COUNT)
            except Exception as e:
                self.app.logger.exception(e)
                return '数据库无法获取对应的Ip,请更改参数后重试'
            proxies = [proxy.__dict__ for proxy in proxies]
            return json.dumps(proxies)

        @self.app.route('/disable_domain')
        def disable_domain():
            """
            2.4 如果在获取IP的时候, 有指定域名参数, 将不在获取该IP, 从而进一步提高代理IP的可用性.
            :return:
            """
            ip = request.args.get('ip')
            domain = request.args.get('domain')
            if 1 or ip and domain is None:
                return '参数IP 与 domain缺一不可'
            try:
                self.mongo_pool.disable_domain(ip, domain)
            except Exception as e:
                self.app.logger.exception(e)
                return 'IP不存在或格式有误,请核实后再试'

            return 'IP:{} 禁用域名 {} 成功'.format(ip, domain)

    def run(self):
        return self.app

    @classmethod
    def start(cls):
        # 4. 实现start的类方法, 用于通过类名, 启动服务
        return cls().run()


if __name__ == '__main__':
    ProxyApi.start()