# -*- coding:utf-8-*-

from conf.conf import *

def get_playbook():
    playbook_path = os.environ.get('PLAYBOOK_PATH')
    if not playbook_path or playbook_path is None:
        playbook_path = FILE_PATH
    return playbook_path

def get_logpath():
    log_path = os.environ.get("LOG_PATH")
    if not log_path or log_path is None:

        if os.path.isdir('/var/log/cloud_monitor/'):pass
        else:
            os.makedirs('/var/log/cloud_monitor/')
        log_path = LOGS_INFO
    return log_path

def get_etcdinfo():
    host = os.environ.get('ETCD_HOST')
    port = os.environ.get('ETCD_PORT')
    protocol = os.environ.get('ETCD_PROTOCOL')
    cert = os.environ.get('ETCD_CERT')
    ca_cert = os.environ.get("ETCD_CA_CERT")
    if not host or host is None:
        host = ETCD_HOST
        port = ETCD_PORT
        protocol = ETCD_HTTP_MODEL
        cert = ETCD_CERT_FILE
        ca_cert = ETCD_CA_CRET_FILE
    return {'host':host,'port':port,'protocol':protocol,'cert':cert,'ca_cert':ca_cert}


def get_rabbitmq():
    host = os.environ.get('RABBITMQ_HOST')
    port = os.environ.get('RABBITMQ_PORT')
    username = os.environ.get('RABBITMQ_USER')
    password = os.environ.get('RABBITMQ_PASSWORD')
    if not host or host is None:
        host = RABBITMQ_HOST
        port = RABBITMQ_PORT
        username = RABBITMQ_USER
        password = RABBITMQ_PASSWORD
    elif not username or username is None:
        username = None
        password = None
    return {'host':host,'port':port,'username':username,'password':password}