#!/usr/bin/python
# -*- coding:utf-8 -*-


from kubernetes import client, config
from kubernetes.client.rest import ApiException
from Adeployment.conf import conf
import kubernetes
import os
from urllib3.exceptions import MaxRetryError


class Kube(object):

    '''connection to K8S server and get all info for K8S cluster'''

    try:
        config.load_kube_config(config_file=os.path.expanduser(conf.K8S_CONFIG_FILE))
    except kubernetes.config.ConfigException:
        pass
    except IOError:
        pass

    def get_node(self):
        '''Get node list and return a dict'''
        node_func = client.CoreV1Api().list_node()
        return node_func

    def read_node(self,node_name):
        node_func = client.CoreV1Api().read_node(node_name)
        return node_func

    def get_list_pod_all_namespaces(self):
        pods_list = client.CoreV1Api().list_pod_for_all_namespaces()
        return pods_list

    def get_list_namespace(self):
        namesapce_list = client.CoreV1Api().list_namespace()
        return namesapce_list

    def get_list_namespaced_pod(self,namespace):
        pods_list = client.CoreV1Api().list_namespaced_pod(namespace)
        return pods_list

    def get_pod_info(self,name,namespace):
        pods_info = client.CoreV1Api().read_namespaced_pod_status(namespace=namespace,name=name)
        return pods_info

    # def get_list_cluster_role(self):
    #     role_list = client.RbacAuthorizationV1Api().list_cluster_role()
    #     return role_list

class KubenetesFunc(Kube):
    ''' 获取内容解析并找到指定内容  Gets content resolution and finds the specified content. '''
    def all_pod_for_namespace(self):
        pod_info = self.get_list_pod_all_namespaces()
        pod_func = self.pod_func(pod_info)
        return pod_func

    def pod_for_namespace(self,namespace):
        pod_info = self.get_list_namespaced_pod(namespace=namespace)
        pod_func = self.pod_func(pod_info)
        return pod_func

    def pod_func(self,pod_info):
        info_dict = {}
        for index, info in enumerate(pod_info.items):
            name = info.metadata.name
            status = info.status.phase
            namespaces = info.metadata.namespace
            restart_count = info.status.container_statuses[0].restart_count
            times = info.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            info_dict.update({index: {'name': name, 'status': status, 'namespace': namespaces,
                                      'restart_count': restart_count, 'time': times}})
        return info_dict

    def pod_info(self,name,namespace):
        pods_info = self.get_pod_info(name=name,namespace=namespace)
        return pods_info

    # def list_cluster_role(self):
    #     role = self.get_list_cluster_role()
    #     print 'userinfo:%s' %role


try:
    kube = Kube()
    kube_func = KubenetesFunc()
    test = Kube().get_node()
except MaxRetryError :
    pass


