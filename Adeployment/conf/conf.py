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

TEST_ADMIN_KEY = "My Secret"
TEST_SERVER = "http://10.10.25.80:8080"
K8S_CONFIG_FILE = "/Users/xunmeng/.kube/.kube/config"
K8S_CONFIG_FILE = "/root/.kube/config"
ETCD_HOST = "10.211.55.9"
ETCD_PORT = 2379
ETCD_HTTP_MODEL = "https"
