# -*- coding:utf-8-*-

from django.shortcuts import render,redirect,HttpResponse
from container.package.logger import logger
from container.package.etcd_module import etcds
from container.package.kube import kube_func,kube
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from Adeployment.core.model_func import save_db
import logging
import json


# Create your views here.
def account_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            save_db.save_logs_to_db("User:%s Login system" % request.user)
            return  redirect(request.GET.get('next') or '/')

    return render(request, 'login.html', locals())

def account_logout(request,**kwargs):
    request.session.clear()
    logout(request)
    return redirect('/')

@csrf_exempt
@login_required
def change_password_obj(request):
    if request.method == 'GET':
        return redirect("/")
    elif request.method == "POST":
        user = request.user
        pwd = request.POST.get('pwd')
        new_pwd = request.POST.get("new_pwd")
        re_pwd = request.POST.get("re_pwd")

        obj = authenticate(username=user,password=pwd)
        # obj = models.UserInfo.objects.filter(username=user, password=pwd).first()
        ret = {'status': True, 'error': None}

        if obj:
            if new_pwd == re_pwd:
                obj.set_password(new_pwd)
                obj.save()
                return HttpResponse(json.dumps(ret))
            else:
                ret['status'] = False
                ret['error'] = "新密码不一致"
                return HttpResponse(json.dumps(ret))
        else:
            ret['status'] = False
            ret['error'] = "原密码错误"
            # 登陆失败，页面显示错误信息
            return HttpResponse(json.dumps(ret))
    return redirect('/')


@login_required
def index(request):
    save_db.save_logs_to_db("User:%s Access index.html" % request.user)
    return render(request,'index.html')

@login_required
def nodes(request):
    logger.logger_info("GET NODE LIST",LOG_LEVEL=logging.INFO,log_type='Nodes')
    save_db.save_logs_to_db("User:%s Get node list" % request.user)
    nodes = kube.get_node()
    return render(request,'nodes/nodes/nodes_list.html',locals())

@login_required
def node_info(request,node_name,*args):
    save_db.save_logs_to_db("User:%s Get node %s info" %(request.user,node_name))
    node_func = kube.read_node(node_name)
    return render(request,'nodes/nodes/nodes_info.html',locals())

@login_required
@csrf_exempt
def pod(request):
    namespace = request.GET.get('project')
    if namespace:
        if namespace == 'all_data':
            save_db.save_logs_to_db("User:%s Get all namespaces" % request.user)
            pod_list = kube_func.all_pod_for_namespace()
        else:
            save_db.save_logs_to_db("User:%s Get namespaces:%s info" %(request.user,namespace))
            pod_list = kube_func.pod_for_namespace(namespace=namespace)
        return HttpResponse(json.dumps(pod_list))
    else:
        save_db.save_logs_to_db("User:%s Get pod list" % request.user)
        pods_list = kube_func.get_list_namespace()
        namespace_list = [name.metadata.name for name in pods_list.items]
        return render(request,'nodes/pods/pods_list.html',locals())


@login_required
def etcd_list(request):
    save_db.save_logs_to_db("User:%s Get etcd list" % request.user)
    leader = etcds.cluster_leader()
    save_db.save_logs_to_db("User:%s Get etcd leader list" % request.user)
    check_port = etcds.check_etcd_port()
    return render(request,'nodes/clusters/etcd_list.html',locals())

@login_required
@csrf_exempt
def etcd_websocket(request):
    logger.logger_info('GET Etcd Info',LOG_LEVEL=logging.INFO,log_type='ETCD')
    save_db.save_logs_to_db("User:%s Use websocket get etcd info" % request.user)
    if request.method == 'POST':
        leader = etcds.cluster_leader()
        check_port = etcds.check_etcd_port()
        save_db.save_logs_to_db("User:%s Use post request of get etcd info success" % request.user)
        logger.logger_info('GET Success',LOG_LEVEL=logging.INFO,log_type='ETCD')
        return HttpResponse(json.dumps({'leader':leader,'port_status':check_port}))
    else:
        save_db.save_logs_to_db("User:%s Get etcd faild,Reason: Use get request" % request.user)
        logger.logger_error('GET faild',LOG_LEVEL=logging.ERROR,log_type='ETCD')
        return HttpResponse(json.dumps({'error':'Access Error'}))


@login_required
def pod_namespace(request):
    namespace = request.GET.get('project').split('=')[0]
    pods_list = kube.get_list_namespaced_pod(namespace)
    save_db.save_logs_to_db("User:%s Get list namespaced pod success" % request.user)
    return render(request, 'nodes/pods/pods_list.html', locals())


@login_required
def pod_info(request,namespace):
    print('pod_info')
    logger.logger_info("get pod info",LOG_LEVEL=logging.INFO,log_type='pod_info')
    name = request.GET.get('pod_name')
    pods_info = kube_func.pod_info(name=name,namespace=namespace)
    save_db.save_logs_to_db("User:%s Get pod:%s info on namespaces:%s " %(request.user,name,namespace))
    return render(request,'nodes/pods/pods_info.html',locals())

@csrf_exempt
@login_required
def namespace(request):
    logger.logger_info('user:%s access namespaces list' % request.user, LOG_LEVEL=logging.INFO, log_type="namespace")
    if request.method == 'POST':
        name = request.GET.get('project')
        if name == 'all_project':
            namespace_info = kube_func.all_namespace_pod_role()
        else:
            namespace_info = kube_func.namespace_pod_role(namespace=name)
        return HttpResponse(json.dumps(namespace_info))
    elif request.method == 'GET':
        return render(request,'nodes/namespace/namespace_list.html',locals())

@login_required
def namespace_info(request):
    namespace = request.GET.get('project').split('=')[0]
    ns_info = kube_func.get_namespace_role_binding(namespace=namespace)
    return render(request,'nodes/namespace/namespace_info.html',locals())

@login_required
def namespace_role_info(request):
    logger.logger_info("user:%s access namespace role info" %request.user,LOG_LEVEL=logging.INFO,log_type='namespace')
    role = request.GET.get('role').split('=')[0]




@login_required
def access_roles(request):
    userList = request.GET.get('roles')
    if userList:
        if userList == 'all_user':
            userFunc = kube_func.get_role_auth()
        else:
            userFunc = kube_func.get_a_role_on_project(userList)
        return HttpResponse(json.dumps(userFunc))
    else:
        userFunc = kube_func.get_all_user_list()
        return render(request,'nodes/roles/roles_list.html',locals())

@login_required
def role_info(request):
    role = request.GET.get('role')
    objects = kube_func.get_a_role_on_project(role)
    userInfo = kube_func.get_a_user_info(role)
    return render(request,'nodes/roles/roles_info.html',locals())

