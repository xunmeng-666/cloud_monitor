# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from Adeployment.admin import site
from Adeployment import forms
from Adeployment.core.model_ansible import build_file
from Adeployment.core.model_func import save_file,delete_file
from Adeployment.core.rabbitmqs import Rabbit_Consumer
from Adeployment.core.logger import logger
from dwebsocket import require_websocket,accept_websocket
import json
import logging
import threading
# Create your views here.

def admin_func():
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name]
        return admin_class

def get_filter_objs(request,admin_class):
    """返回filter的结果queryset"""

    filter_condtions = {}
    for k,v in request.GET.items():
        if k in ['_page','_q','_o']:
            continue
        if v:#valid condtion
            filter_condtions[k] = v

    queryset = admin_class.model.objects.filter(**filter_condtions)
    return queryset,filter_condtions

def get_search_objs(request,querysets,admin_class):
    """
    1.拿到_q的值
    2.拼接Q查询条件
    3.调用filter(Q条件)查询
    4. 返回查询结果
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    q_val = request.GET.get('_q') #None
    if q_val:
        q_obj = Q()
        q_obj.connector = "OR"
        for search_field in admin_class.search_fields: #2
            q_obj.children.append( ("%s__contains" %search_field,q_val) )

        search_results = querysets.filter(q_obj)#3
    else:
        search_results = querysets

    return search_results,q_val

def get_orderby_objs(request,querysets):
    """
    排序
    1.获取_o的值
    2.调用order_by(_o的值)
    3.处理正负号，来确定下次的排序的顺序
    4.返回
    :param request:
    :param querysets:
    :return:
    """
    orderby_key = request.GET.get('_o') #-id
    last_orderby_key = orderby_key or ''
    if orderby_key:
        order_column = orderby_key.strip('-')
        order_results = querysets.order_by(orderby_key)
        if orderby_key.startswith('-'):
            new_order_key = orderby_key.strip('-')
        else:
            new_order_key = "-%s"% orderby_key

        return order_results,new_order_key,order_column,last_orderby_key
    else:
        return querysets,None,None,last_orderby_key

@login_required
def deploy(request,no_render=False):
    logger(request,logging.INFO)
    page_name = "DeployMent"
    admin_class = admin_func().get('files')
    deployfunc = admin_func().get('deploylist').model.objects.values('id', 'name')
    model_name = admin_class.model._meta.verbose_name
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "POST":  # admin action
        action_func_name = request.POST.get('admin_action')
        action_func = getattr(admin_class, action_func_name)
        selected_obj_ids = request.POST.getlist("_selected_obj")
        selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
        action_res = action_func(request, selected_objs)
        if action_res:
            return action_res
        return redirect(request.path)
    else:
        form_obj = form()
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            querysets = paginator.page(1)
        except EmptyPage:
            querysets = paginator.page(paginator.num_pages)

    if no_render:
        return locals()
    else:
        return render(request, 'cluster/deploy/deploy.html', locals())

@login_required
@csrf_exempt
def deploy_del(request):
    admin_class = admin_func().get('files')
    if request.method == 'GET':
        for get_id in request.GET.get('idAll').split(','):
            obj = admin_class.model.objects.get(id=get_id)
            filefunc = admin_class.model.objects.values('file_name', 'file_path', 'create_date').get(id=get_id)
            file_name = "%s%s-%s" % (filefunc['file_path'], filefunc['file_name'], filefunc['create_date'].strftime("%Y-%m-%d_%H:%M:%S"))
            delete_file(file_name)
            obj.delete()
            logger('用户删除文件:%s' %(file_name),logging.INFO)
        return redirect('/deployment/')
    elif request.method == 'POST':
        try:
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                filefunc = admin_class.model.objects.values('file_name', 'file_path', 'create_date').get(id=get_id)
                file_name = "%s%s-%s" % (filefunc['file_path'],
                                         filefunc['file_name'], filefunc['create_date'].strftime("%Y-%m-%d_%H:%M:%S"))
                delete_file(file_name)
                obj.delete()
            return HttpResponse(json.dumps({"status": 'true'}))
        except ValueError:
            pass
        return HttpResponse(json.dumps({"status": 'true'}))

@login_required
@csrf_exempt
def deploy_delfile(request):
    admin_class = admin_func().get('deploylist')
    if request.method == 'GET':
        for get_id in request.GET.get('idAll').split(','):
            obj = admin_class.model.objects.get(id=get_id)
            filefunc = admin_class.model.objects.values('file_name', 'file_path', 'create_date').get(id=get_id)
            file_name = "%s%s-%s" % (filefunc['file_path'],
                                     filefunc['file_name'], filefunc['create_date'].strftime("%Y-%m-%d_%H:%M:%S"))

            delete_file(file_name)
            obj.delete()
            logger('用户删除文件:%s' % (file_name), logging.INFO)
        return redirect('/deployment/')
    elif request.method == 'POST':
        try:
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                filefunc = admin_class.model.objects.values('name').get(id=get_id)
                file_name = "%s" % (filefunc['name'])
                delete_file(file_name)
                obj.delete()
            return HttpResponse(json.dumps({"status": 'true'}))
        except ValueError:
            pass
        return HttpResponse(json.dumps({"status": 'true'}))


@login_required
@csrf_exempt
def deploy_file(request):
    logger('%s' % (request), logging.INFO)
    ret = {'status': 'true', 'error': 'false'}
    if request.method == 'POST':
        admin_class = admin_func().get('files')
        inven_id = request.GET.get('inventory_id').split('=')[0]
        playb_id = request.GET.get('playbook_id').split('=')[0]
        t = threading.Thread(build_file(inven_id,playb_id,admin_class))
        t.start()
        t.join(10)
        ret.update({'status': 'false','error': 'true'})
        return HttpResponse(json.dumps(ret))
    return HttpResponse(status=404)


@login_required
@csrf_exempt
def upload(request):
    logger('%s' % (request), logging.INFO)
    ret = {'status':'true'}
    if request.method == 'POST':
        filename = request.FILES.get('filename')
        filetype = request.GET.get('file_type')
        logger('用户上传文件:%s' %filename, logging.INFO)
        logger('用户上传文件类型:%s' %filetype, logging.INFO)
        if save_file(filename=filename,filetype=filetype):
            logger('保存成功', logging.INFO)
            return HttpResponse(json.dumps(ret))
        logger('保存失败', logging.INFO)
        ret.update({'status':'false','error': 'true'})
        return HttpResponse(json.dumps(ret))

@login_required
@csrf_exempt
def template(request,no_render=False):
    logger(request, logging.INFO)
    admin_class = admin_func().get('filetype')
    model_name = admin_class.model._meta.verbose_name
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == 'POST':
        form_obj = form(data=request.POST)
        logger('用户增加文件类型:%s' %form_obj, logging.INFO)
        if form_obj.is_valid():
            logger('保存成功', logging.INFO)
            form_obj.save()
            # return {'status':'success'}
            return redirect('/deployment/file_types/' ,locals())
    else:
        form_obj = form()
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            querysets = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            querysets = paginator.page(paginator.num_pages)

    if no_render:  # 被其它函数调用，只返回数据
        return locals()
    else:
        return render(request, 'cluster/deploy/template.html', locals())

@login_required
@csrf_exempt
def template_del(request):
    logger('%s' %request, logging.INFO)
    ret = {'status': 'true', 'error': 'false'}
    try:
        if request.method =='POST':
            admin_class = admin_func().get('filetype')
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                obj.delete()
                logger('删除成功', logging.INFO)
            return HttpResponse(json.dumps(ret))
    except ValueError:
        pass
    return HttpResponse(json.dumps(ret))

@login_required
@csrf_exempt
def template_delete(request):
    logger(request, logging.INFO)
    admin_class = admin_func().get('filetype')
    for get_id in request.GET.get('idAll').split(','):
        obj = admin_class.model.objects.get(id=get_id)
        obj.delete()
        logger('删除成功', logging.INFO)
    return redirect('/deployment/file_types/')

@login_required
@require_websocket
def echo_logs(request):
    logger(request, logging.INFO)
    msg = request.websocket.wait()
    print 'msg:',msg
    if msg == 'quit':
        run_mq = Rabbit_Consumer()
        run_mq.rabbit_close()
    elif msg == 'file':
        logs_name = request.GET.get('LogName')
        file = open(logs_name, 'r')
        for content in file.readlines():
            request.websocket.send(content.encode('utf-8'))
        file.close()
        request.websocket.close()
    elif msg == 'logs':
        admin_class = admin_func().get('deploylist')
        log_name = admin_class.model.objects.all().values('name').order_by('-id')[0]['name']
        file = open(log_name,'r')
        for content in file.readlines():
            request.websocket.send(content.encode('utf-8'))
        file.close()
        request.websocket.close()
    else:
        run_mq = Rabbit_Consumer()
        run_mq.rabbit_consumer(request)

@login_required
def settings(request,no_render=None):
    admin_class = admin_func().get('settings')
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "POST":
        form_obj = form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/deployment/settings/')

    elif request.method == "GET":
        form_obj = form()
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            querysets = paginator.page(1)
        except EmptyPage:
            querysets = paginator.page(paginator.num_pages)

    if no_render:
        return locals()
    else:
        return render(request, 'settings/settings.html', locals())


@csrf_exempt
def del_settings(request):
    logger('%s' % request, logging.INFO)
    ret = {'status': 'true', 'error': 'false'}
    try:
        if request.method == 'POST':
            admin_class = admin_func().get('settings')
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                obj.delete()
                logger('删除成功', logging.INFO)
            return HttpResponse(json.dumps(ret))
    except ValueError:
        pass
    return HttpResponse(json.dumps(ret))