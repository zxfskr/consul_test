# consul_test

```
consul_test/
├── consul.ctmpl                 # 修改consul-template配置
├── consul_deregister_test.py    # 删除服务foo
├── consul_main.py               # 测试服务是否正常
├── consul_register_test.py      # 注册服务foo
├── flask_test.py                # foo服务程序
├── README.md
└──  requirements.txt
```

## 一、确认软件安装

0. 更新软件库
```
sudo apt update
```

1. 安装docker
```
wget -qO- https://get.docker.com/ | sh
```

2. 安装consul
```
sudo docker pull consul:latest
```

3. python使用python3.5
```
python3 --version
Python 3.5.3
```

4. 安装pip3

```
sudo apt-get install python3-pip
```

5. 更新pip3

```
sudo pip3 install --upgrade pip
```

## 二、安装和使用虚拟环境

- 安装虚拟环境管理工具

```
sudo pip3 install virtualenv
```

- 安装虚拟环境管理扩展包

```
sudo pip3 install virtualenvwrapper 
```

- 编辑家目录下面的.bashrc文件，添加下面几行。

```
if [ -f /usr/local/bin/virtualenvwrapper.sh ]; then
  export WORKON_HOME=$HOME/.virtualenvs
  export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
  source /usr/local/bin/virtualenvwrapper.sh
fi
```

- 使用以下命令使配置立即生效

```
source ~/.bashrc
```

- 创建虚拟环境命令(**需要连网**)：

```
# 创建python2虚拟环境：
mkvirtualenv 虚拟环境名

# 创建python3虚拟环境：
mkvirtualenv --python=/usr/bin/python3 consul_test
```

- 进入虚拟环境工作：

```
workon 虚拟环境名
```

- 查看机器上有哪些虚拟环境：

```
workon
```

- 退出虚拟环境：

```
# 使失效
deactivate  
```

- 删除虚拟环境：

```
rmvirtualenv 虚拟环境名
```

## 三、Git安装与配置

1. 安装git

```
sudo apt-get install git
```

2. 设置git用户名和邮箱

```
git config --global user.name "Your Name"
git config --global user.email "youremail@example.com"
```

3. 生成ssh公私钥对

```
ssh-keygen -t rsa -C youremail@example.com
```

4. 将公钥id_rsa.pub内容拷贝一份到GitLab设置中的SSH Keys中

## 四、部署步骤

1. 在家目录下创建workspace文件夹

```
mkdir ~/workspace
cd ~/workspace
```

2. 克隆项目

```
git clone git@gitlab.using.site:zhangxf/consul_test.git
```

3. 进入虚拟环境，根据不同的模块，安装相应的依赖包

```bash
cd consul_test
workon consul_test
pip install -r requirements.txt
```

## 五、平台运行

- 以3台机器为例，host分别为

```
172.16.81.1 node1
172.16.81.130 node2
172.16.81.129 node3
```

- 启动docker中的consul，推荐集群中有3到5个server，首先启动第一个server，设置为leader
```
sudo docker run -d --name=node1 --restart=always --net=host \
-e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' \
consul agent -server -bind=172.16.81.1 \
-bootstrap -node=node1 \
-data-dir=/tmp/data-dir -client 0.0.0.0 -ui
```
docker run参数：
```
-d
  后台运行
--name=node1
  设置容器名
--restart=always
  容器停止时，自动重启容器
--net=host
  容器使用实体机ip
-e  
设置环境变量'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}'设置节点退出时不发送leave信号，保留raft peers list each.
```

consul agent 参数
```
-server
  以server模式启动
-bind=172.16.81.1
  绑定本机ip
-bootstrap
  不执行选举，直接本机启动时为leader
-retry-join=172.16.81.1
  加入一个集群
-retry-interval=30s 
  join失败时重连间隔
-retry-max=0
  join失败时重连次数，0为不限次数。
-node=node1
  设置node_name
-data-dir=/tmp/data-dir
  数据存储目录
-client 0.0.0.0 -ui
  web ui绑定本机ip
```

- 启动第二个consul，加入集群

```
sudo docker run -d --name=node2 --restart=always --net=host \
-e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' \
consul agent -server -bind=172.16.81.131 \
-retry-join=172.16.81.1 -retry-interval=30s -retry-max=0 \
-node=node2 \
-data-dir=/tmp/data-dir -client 0.0.0.0 -ui
```

- 启动第三个consul，加入集群

```
sudo docker run -d --name=node3 --restart=always --net=host \
-e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' \
consul agent -server -bind=172.16.81.129 \
-retry-join=172.16.81.131 -retry-interval=30s -retry-max=0 \
-node=node3 -client 0.0.0.0 -ui
```

- 访问任意一个节点的web ui,可以看到正常运行的三个节点

![Aaron Swartz](https://github.com/zxxxf/consul_test/raw/master/img/consul_cluster.png)

- 使用模块python-consul通过api进行服务注册。在每个server上启动测试服务并注册。

```
#注册服务
python consul_register_test.py
#启动测试服务
python flask_test.py
```

register api：
```
c = consul.Consul(host=consul_host, port=consul_port)
service_id="foo"+consul_host
addr = "http://{0}:{1}".format(consul_host, '10000')
c.agent.service.register(
    "foo",
    service_id=service_id,
    address=consul_host,
    port=10000,
    # ttl="10s"
    check=Check.http(addr, "10s", deregister="90ms"),
)

```

deregister api：
```
c = consul.Consul(host=consul_host, port=consul_port)
c.agent.service.deregister(service_id)
```

- 打开web ui查看已经注册的服务状况

![Aaron Swartz](https://github.com/zxxxf/consul_test/raw/master/img/consul_services.png)

- 选取一个节点作为客户端，以node1为例安装nginx和consul-template

```
#下载最新版本：
wget http://nginx.org/download/nginx-1.13.6.tar.gz
#解压：
tar -zxvf nginx-1.13.6.tar.gz
#进入解压目录：
cd nginx-1.13.6
#配置：
./configure --prefix=/usr/local/nginx 
#编译：
make
#安装：
sudo make install
#修改配置文件
cd /usr/local/nginx/conf
#在nginx.conf的http模块添加以下语句
include       conf.d/*.conf;
#新建consul测试配置文件夹
sudo mkdir conf.d/
sudo touch conf.d/test.conf
#启动：
sudo /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
注意：-c 指定配置文件的路径，不加的话，nginx会自动加载默认路径的配置文件，可以通过-h查看帮助命令。
#查看进程：
ps -ef | grep nginx

#下载consul-template

wget https://releases.hashicorp.com/consul-template/0.20.0/consul-template_0.20.0_linux_amd64.zip

unzip consul-template_0.20.0_linux_amd64.zip

mv consul-template /usr/local/bin/

# 启动consul-template
cd ~/workspace/consul_test
sudo consul-template -template "./consul.ctmpl:/usr/local/nginx/conf/conf.d/test.conf:sudo /usr/local/nginx/sbin/nginx -s reload"
```

- 测试操作

此时可以访问172.16.81.1：9000访问web ui

![Aaron Swartz](https://github.com/zxxxf/consul_test/raw/master/img/consul_nginx_web_ui.png)

测试服务是否正常执行，此程序会向服务发送任务。
```
python consul_main.py
```
