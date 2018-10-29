# -*- coding:utf-8-*-

import socket
import etcd
from Adeployment.core.model_func import get_db
from Adeployment.core.environments import get_etcdinfo
from conf import conf


class EtcdModel(object):
    def __init__(self):
        func = get_etcdinfo()
        self.host = func['host']
        self.port = func['port']
        self.model = func['protocol']
        self.cert = func['cert']
        self.ca_cert = func['ca_cert']
        self.client = etcd.Client(host=self.host,port=self.port,protocol=self.model,
                                  ca_cert=self.ca_cert,cert=self.cert,read_timeout=5)

        # self.client = etcd.Client(host='192.168.51.3', port=2379, protocol='https', ca_cert='/root/.kube/etcd/ca.crt',
        #                      cert=('/root/.kube/etcd/peer.crt', '/root/.kube/etcd/peer.key'))



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
            except Exception:
                host_info.update({'status':'Error'})
        return host_list

etcds = EtcdModel()
