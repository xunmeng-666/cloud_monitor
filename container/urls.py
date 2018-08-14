# -*- coding:utf-8-*-
from django.conf.urls import url,include
from django.contrib import admin
from container import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^etcd/$',views.etcd_list),
    url(r'^etcd_info/$',views.etcd_websocket),
    url(r'^pods/$',views.pod),
    url(r'^pods/namespace/$',views.pod_namespace),
    url(r'^pods/(\w+)/$',views.pod_info),
    url(r'^nodes/$',views.nodes),
    url(r'^nodes/node_info/([\w.]+)/$',views.node_info),
    url(r'^cluster_node/$',views.master_cluster),
]