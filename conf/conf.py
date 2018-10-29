# -*- coding:utf-8-*-
import os
import datetime

#定义配置文件路径
BASH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#LOG配置
LOG_NAME = "ADAdmin"
LOGS = "/var/log/cloud_monitor/%s" %(LOG_NAME)
LOGS_INFO = "/var/log/cloud_monitor/cloudfly_info.log"
LOGS_ERROR = "/var/log/cloud_monitor/cloudfly_error.log"
FILE_PATH = "/etc/ansible/roles/"

#RabbitMQ配置
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = None
RABBITMQ_PASSWORD = None

TEST_ADMIN_KEY = "My Secret"
TEST_SERVER = ""
# K8S_CONFIG_FILE = "/Users/xunmeng/.kube/.kube/config"
K8S_CONFIG_FILE = "/root/.kube/config"
ETCD_HOST = "192.168.51.3"
ETCD_PORT = 2379
ETCD_HTTP_MODEL = "https" #如果启用HTTPS，必须配置证书文件
#配置ETCD_PEER_CERT_FILE和ETCD_PEER_KEY_FILE文件,证书文件必须是绝对路径
ETCD_CA_CRET_FILE = "/root/.kube/etcd/ca.crt"
ETCD_CERT_FILE = ("/root/.kube/etcd/peer.crt","/root/.kube/etcd/peer.key")