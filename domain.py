from IPProxyPool.settings import MAX_SCORE

# 代理ip的模型类
class Proxy(object):
    def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, area=None, score=MAX_SCORE, disable_domains=[]):
        # IP: 代理的Ip地址
        self.ip = ip
        # port: 代理IP的端口号
        self.port = port
        # protocol: 代理Ip支持的协议类型, http:0, https:1, http,https:2
        self.protocol = protocol
        # nick_type: 代理IP的匿名程度,  高匿:0, 匿名:1, 透明:2
        self.nick_type = nick_type
        # speed: 代理IP的响应速度, 单位s
        self.speed = speed
        # area: 代理IP所在区
        self.area = area
        # score: 代理IP的评分, 用于衡量代理的可用性
        self.score = score
        # disable_domains: 不可用的域名列表,  有些代理IP在某些域名下不可用,但在其他域名下可用
        self.disable_domains = disable_domains

    # 提供一个 __str__方法, 返回字符串
    def __str__(self):
        # 返回数据字符串
        return str(self.__dict__)