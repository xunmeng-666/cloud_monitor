# -*- coding:utf-8-*-
from django.conf.urls import url,include
from django.contrib import admin
from container import views


urlpatterns = [
    url(r'^etcd/$',views.etcd_list),
    url(r'^etcd_info/$',views.etcd_websocket),
    url(r'^pods/$',views.pod),
    url(r'^pods/namespace/$',views.pod_namespace),
    url(r'^pods/(\w+)/$',views.pod_info),
    url(r'^namespace/',views.namespace),
    url(r'^namespace-info/',views.namespace_info,name='namespace-info'),
    url(r'^namespace-info/info/',views.namespace_role_info,name='namespace-role-info'),
    url(r'^roles/$',views.access_roles,name='role_list'),
    url(r'^roles/info/$',views.role_info,name='role_info'),
    url(r'^nodes/$',views.nodes),
    url(r'^nodes/node_info/([\w.]+)/$',views.node_info),
]