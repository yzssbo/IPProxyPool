
from IPProxyPool.core.proxy_api import ProxyApi

app = ProxyApi.start()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6000, debug=False)
