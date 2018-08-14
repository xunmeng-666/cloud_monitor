from django.shortcuts import render,redirect,HttpResponse
from container.package.logger import logger
from container.package.etcd_module import etcds
from container.package.kube import kube_func,kube
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from dwebsocket import require_websocket,accept_websocket
import etcd
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
            return  redirect(request.GET.get('next') or '/')

    return render(request, 'login.html', locals())

def account_logout(request,**kwargs):
    request.session.clear()
    logout(request)

    return redirect('/')

@login_required
def index(request):
    return render(request,'index.html')

@login_required
def nodes(request):
    logger.logger_info("GET HOST LIST",LOG_LEVEL=logging.INFO,log_type='Nodes')
    nodes = kube.get_node()
    return render(request,'nodes/nodes/nodes_list.html',locals())

@login_required
def node_info(request,node_name,*args):
    node_func = kube.read_node(node_name)
    return render(request,'nodes/nodes/nodes_info.html',locals())

@login_required
@csrf_exempt
def pod(request):
    if request.method == 'GET':
        pods_list = kube.get_list_pod_all_namespaces
        return render(request,'nodes/pods/pods_list.html',locals())

    elif request.method == 'POST':
        namespace = request.GET.get('project')
        if namespace == 'all_data':
            pod_list = kube_func.all_pod_for_namespace()
        else:
            pod_list = kube_func.pod_for_namespace(namespace=namespace)
        return HttpResponse(json.dumps(pod_list))

@login_required
def etcd_list(request):

    leader = etcds.cluster_leader()
    check_port = etcds.check_etcd_port()
    return render(request,'nodes/clusters/etcd_list.html',locals())

@login_required
@csrf_exempt
def etcd_websocket(request):
    logger.logger_info('GET Etcd Info',LOG_LEVEL=logging.INFO,log_type='ETCD')
    if request.method == 'POST':
        leader = etcds.cluster_leader()
        check_port = etcds.check_etcd_port()
        logger.logger_info('GET Success',LOG_LEVEL=logging.INFO,log_type='ETCD')
        return HttpResponse(json.dumps({'leader':leader,'port_status':check_port}))
    else:
        logger.logger_error('GET faild',LOG_LEVEL=logging.ERROR,log_type='ETCD')
        return HttpResponse(json.dumps({'error':'Access Error'}))


@login_required
def pod_namespace(request):
    namespace = request.GET.get('project').split('=')[0]
    pods_list = kube.get_list_namespaced_pod(namespace)
    return render(request, 'nodes/pods/pods_list.html', locals())


@login_required
def pod_info(request,namespace):

    logger.logger_info("get pod info",LOG_LEVEL=logging.INFO,log_type='pod_info')
    name = request.GET.get('pod_name')
    pods_info = kube_func.pod_info(name=name,namespace=namespace)
    return render(request,'nodes/pods/pods_info.html',locals())


def master_cluster(request):
    pass

