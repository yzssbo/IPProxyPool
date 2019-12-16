# IP代理池

### 介绍

从一堆不稳定代理IP中,抽取高可用代理IP, 给爬虫使用

### 软件架构

代理池开发环境

- 开发语言： Python3
- 重要字段:
  - protocol: 代理IP支持的协议类型,http是0, https是1, https和http都支持是2
  - nick_type: 代理IP的匿名程度, 高匿:0, 匿名: 1, 透明:2
  - score: 代理IP的评分, 用于衡量代理的可用性;
  - disable_domains: 不可用域名列表
- 五大核心模块
  - 代理IP采集模块: 采集代理IP, 把可用代理IP, 入库
  - 校验模块: 检测代理的可用性: 响应速度, 协议类型, 匿名程度
  - 数据库模块: 对代理IP进行增删改查的操作
  - 检测模块: 获取数据库中代理IP, 进行处理, 保证代理IP的可用性
  - API模块: 提供爬虫或高可用代理IP 和 指定代理不可用域名的接口.
- 主要技术：
  - requests
  - lxml
  - pymongo
  - Flask

### 安装教程

##### 安装虚拟环境

项目部署的系统是ubuntu18.04


##### python 虚拟环境
pip3 install virtualenv 
##### 封装了虚拟环境，支持一些简化命令
pip3 install virtualenvwrapper

注：新的服务器中没有pip命令需要使用 sudo apt—get install python3-pip 进行安装后再执行上方操作


##### 添加环境变量：
vim ~/.profile
##### 在末尾添上下面的语句
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3

export WORKON_HOME=$HOME/.virtualenvs

source ~/.local/bin/virtualenvwrapper.sh

执行一下~/.profile ：
source ~/.profile


##### 创建虚拟环境
mkvirtualenv 虚拟环境名称 -p python3
##### 完成创建后自动进入虚拟环境
##### 查看所有虚拟环境
workon 两次tab键
##### 切入到某一个虚拟环境
workon 虚拟环境名称
##### 退出虚拟环境
deactivate


##### 安装mongodb
sudo apt-get install mongodb
在终端输入`mongo`，然后回车进入数据库 


##### 安装依赖库
pip install -r requerments.txt


### 代理IP池的使用

##### 1. `main.py`启动项目  

   ###### main.py文件说明
   main.py文件集合了proxy_test， run_spider， FlaskAPi三大模块，对外提供flask服务接口，内部爬虫模块与ip检测模块使用schedule每隔一定时间会自动执行，执行时间间隔可以在setting.py文件中自行更改
   ###### 正常启动  启动后三个模块会同时启动，爬虫模块与检测模块执行结束后会等待时间间隔再次执行
   python3 main.py
   
   ###### 服务器后台持续运行
   nohup python3 main.py

##### 2. `proxy_api.py`：IP池接口文件，返回ip

##### 3. 项目使用flask服务开启接口
   ###### 本地IP获取方法
   ###### 获取随机一个http类型的高匿ip, 一般domain可以不带， nike_type尽量选择为2， 0与1一般爬取到的ip不为此类型
   127.0.0.1/random?protocol=http&nick_type=2&domain=taobao.com
   ###### 获取最大数量的一批https类型的高匿ip 同上
   127.0.0.1/proxies?protocol=https&nick_type=2
   ###### 在使用过程中如果遇到某个ip在爬取对应域名（taobao.com)不能访问时，此时对应ip会被标记为淘宝不可用，下次在筛选ip时会过滤掉ip的disable_domain中含有taobao的
   127.0.0.1/disable_domain?ip=*.*.*.*domain=taobao.com
   
   ### 接口参数说明
   --protocol='支持http的协议 可选 http/https
   --nick_type='ip类型，可选0/1/2， 0 是透明 1是匿名 2是高匿'
   --domains='代表你要在哪个域名下使用ip， 例如taobao.com， 那么会自动过滤掉对淘宝不好用的ip'
   
   

   ### 接口调用案例
   import requests
   response = requests.get(url='http://xxx.xxx.xxx.xxx:16688/random?protocol=htttp&nick_type=2')

   data = response.content.decode()
   print(data)  #  http://47.98.176.205:8118
   
   
   
   
   ### 觉得麻烦懒得看？没关系直接使用我已经部署好的地址
   
   http://118.25.93.211:16688/random?protocol=https&nick_type=2
   
   http://118.25.93.211:16688/proxies?protocol=https&nick_type=2

