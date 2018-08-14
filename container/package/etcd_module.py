# -*- coding:utf-8-*-

import etcd
import socket
from Adeployment.conf import conf
from Adeployment.core.model_func import get_db

class EtcdModel(object):
    def __init__(self):

        self.host = conf.ETCD_HOST
        self.port = conf.ETCD_PORT
        self.model = conf.ETCD_HTTP_MODEL
        if not self.host or self.host is None:
            try:
                func = get_db.get_setting().model.objects.values('name','ipaddress','ports','model')
                self.host = func[0]['ipaddress']
                self.port = int(func[0]['ports'])
                self.model = func.model.Choices[func[0]['model']][1]
            except IndexError:
                self.host = None
                self.port = None
                self.model = None

    def connect(self):
        self.client = etcd.Client(host=self.host,port=self.port,protocol=self.model,read_timeout=5)

    def node_list(self):
        nodes_list = self.client.members
        return nodes_list

    def cluster_version(self):
        cluster_version = self.client.cluster_version

        return cluster_version

    def cluster_leader(self):
        cluster_leader = self.client.leader
        return cluster_leader

    def check_etcd_port(self):
        host = self.node_list()
        host_list = []
        for i in host:
            ids = host[i].get('id')
            name = host[i].get('name')
            hosts = host[i].get('clientURLs')[0].split('//')[1].split(':')[0]
            ports = host[i].get('clientURLs')[0].split('//')[1].split(':')[1]
            host_list.append({'id':ids,'name':name,'host':hosts,'port':ports,'status':None})
        check_status = self.socket_check(host_list)
        return check_status

    def socket_check(self,host_list):
        for host_info in host_list:
            ip = host_info.get('host')
            port = int(host_info.get('port'))
            sk = socket.socket()
            try:
                sk.connect((ip,port))
                host_info.update({'status':'OK'})
                sk.close()
            except ConnectionRefusedError:
                host_info.update({'status':'Error'})
        return host_list

etcds = EtcdModel()
