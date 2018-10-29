#!/usr/bin/python
# -*- coding:utf-8 -*-


import os

import kubernetes
from kubernetes import client, config
from urllib3.exceptions import MaxRetryError
from conf import conf
from openshift import config as _config
from openshift import client as _client
import openshift.client as oclient


class Kube:
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

    def get_namespace_role_binding(self,namespace):
        role = client.RbacAuthorizationV1Api().list_namespaced_role_binding(namespace)
        return role

    def get_role_binding_for_all_namespace(self):
        role = client.RbacAuthorizationV1Api().list_role_binding_for_all_namespaces()
        return role

    def get_list_cluster_role_binding(self):
        '''获取所有绑定权限的用户，如：admin权限'''
        role = client.RbacAuthorizationV1Api().list_cluster_role_binding()
        return role

class OpenShiftFunc:
    ''' 启用openshift模块，处理kubernetesAPI无法处理的功能'''

    def get_a_user_create_time(self):
        '''收集所有用户信息'''
        all_user = oclient.OapiApi().list_identity()
        return all_user

    def get_all_project(self):
        '''使用OpenShift API获取所有项目'''
        all_project = oclient.ProjectOpenshiftIoV1Api().list_project()
        return all_project

    def get_all_role(self):
        '''获取所有用户信息，不包含系统创建用户'''
        all_role = oclient.UserOpenshiftIoV1Api().list_identity()
        return all_role




class KubenetesFunc(Kube,OpenShiftFunc):
    ''' 获取内容解析并找到指定内容  Gets content resolution and finds the specified content. '''

    def list_namespace(self):
        ''' Get all namespace and return all namespace list'''
        all_namespace = self.get_list_namespace()
        ns_name = [name.metadata.name for name in all_namespace.items]
        return ns_name

    def all_pod_for_namespace(self):
        pod_info = self.get_list_pod_all_namespaces()
        pod_func = self.pod_func(pod_info)
        return pod_func

    def pod_for_namespace(self,namespace):
        ''' GET all pod for a namespace,and get pod info for function pod_func'''
        pod_info = self.get_list_namespaced_pod(namespace=namespace)
        pod_func = self.pod_func(pod_info)
        return pod_func

    def pod_func(self,pod_info):
        '''Get pod info for a namespace '''
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

    def pod_count(self,namespace):
        '''Get pod count for a namespace'''
        count = 0
        podlist = self.get_list_namespaced_pod(namespace=namespace)
        for pod_name in podlist.items:
            if pod_name.metadata.name:
                count += 1
        return count

    def resolve_namespace_role(self,namespace):
        '''
        : Get a namespace kind and name return a dict
        :param namespace:
        :return:
        '''
        role_dict = {}
        role = self.get_namespace_role_binding(namespace)
        for info in role.items:
            for subject in info.subjects:
                if subject.kind == 'User' or subject.kind == 'ServiceAccount':
                    role_dict.update({'name':subject.name,'kind':subject.kind,'namespace':namespace,'create_date':dateFunc(info.metadata.creation_timestamp)})
                    return role_dict

    def all_namespace_pod_role(self):
        ''' Get pod count and role for all namespace '''
        name_list = self.list_namespace()
        namespace_dict = {}
        for namespace in name_list:
            pod_count = self.pod_count(namespace)
            role_list = self.resolve_namespace_role(namespace)
            namespace_dict.update({namespace:{'pod_count':pod_count,'login_user':role_list}})
        return namespace_dict

    def namespace_pod_role(self,namespace):
        ''' Get pod count and role for a namespace '''
        namespace_dict = {}
        pod_count = self.pod_count(namespace)
        role_list = self.resolve_namespace_role(namespace)
        namespace_dict.update({namespace: {'pod_count': pod_count, 'login_user': role_list}})
        return namespace_dict

    def get_all_role_on_project(self):
        '''关联用户与项目'''
        role = {ro.user.name:[{"create_date":dateFunc(ro.metadata.creation_timestamp),'provider_name':ro.provider_name}] \
                for ro in self.get_all_role().items}
        for key,value in role.items():
            pro_list = []
            for ns in self.get_all_project().items:
                if ns.metadata.annotations.get('openshift.io/requester') == key:
                    pro_list.append(self.namespace_pod_role(ns.metadata.name))
            value[0].update({'namespace':pro_list})
        return role

    def get_role_auth(self):
        ''' 获取手动创建用户权限'''
        cluster_role_dict = {}
        role_dict = self.get_all_role_on_project()
        cluster_role = self.get_list_cluster_role_binding()
        try:
            for ns in cluster_role.items:
                for i in ns.subjects:
                    cluster_role_dict.update({i.name:[{'kind':i.kind,'name':ns.metadata.name,
                                                       'create_date':dateFunc(ns.metadata.creation_timestamp)}]})
        except TypeError:
            pass

        for ro in cluster_role_dict:
            if ro in role_dict:
                # role_dict[ro][0].update({'kind':cluster_role_dict[ro][0]['kind'],'name':cluster_role_dict[ro][0]['name']})
                role_dict[ro][0].update({'kind':cluster_role_dict[ro][0]})

        return role_dict

    def get_a_role_on_project(self,role):
        '''返回单个用户项目信息'''
        _role = {key:value for key,value in self.get_role_auth().items() if key == role}

        return _role

    def get_all_user_list(self):
        '''获取用户列表，前端展示使用'''
        user_list = [user.user.name for user in self.get_all_role().items]
        return user_list

    def get_a_user_info(self,name):
        '''获取单个用户JSON格式信息'''
        userFunc = self.get_all_role()
        userObj = {name:info for info in userFunc.items if info.user.name == name}
        userObj[name].metadata.namespace = kube_func.get_a_role_on_project(name)[name][0]['namespace']
        return userObj


def dateFunc(date):
    if type(date) is list:
        for i in date:
            if i is None or not i:return None
            else:return i.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return date.strftime("%Y-%m-%d %H:%M:%S")

try:
    kube = Kube()
    kube_func = KubenetesFunc()
    test = Kube().get_node()
except MaxRetryError :
    pass

# aa = Kube().get_list_cluster_role()
