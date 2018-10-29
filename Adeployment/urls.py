# -*- coding:utf-8-*-

from django.conf.urls import url,include
from Adeployment import views


urlpatterns = [
    url(r'^$', views.deploy),
    url(r'^upload/$', views.upload),
    url(r'^del/$', views.deploy_del),
    url(r'^del_logfile/$', views.deploy_delfile),
    # url(r'^file/$', views.deploy_file),
    url(r'^type_del/$', views.template_delete),
    url(r'^types_del/$', views.template_del),
    url(r'^echo_logs/$', views.echo_logs),
    url(r'^settings/$', views.settings),
    url(r'^file_types/$', views.template),
    url(r'^system/logs/$', views.system_logs),
    url(r'^settings/del_settings/$', views.del_settings,name='del_settings'),

]