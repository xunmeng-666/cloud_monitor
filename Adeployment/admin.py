#!/usr/bin/python
# -*- coding: utf-8 -*-

# Register your models here.

from Adeployment import models
from Adeployment.admin_base import site,BaseAdmin


class GroupInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["组名"]
    search_fields = ['name']


class VersionInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ['版本号']
    search_fields = ['name']

class DeplayLogsInfoAdmin(BaseAdmin):
    list_display = ('name')
    list_filter = ['名称']

class FilesInfoAdmin(BaseAdmin):
    list_display = ("name",'file_path','file_type','create_date')
    list_filter =  ["文件名","保存路径","文件类型","创建时间"]
    search_fields = ['name','file_type']

class HostInfoAdmin(BaseAdmin):
    list_display = ('hostname','address','port','username','password','group','version','script')
    list_filter = ["主机名",'IP地址','SSH端口号','用户名','密码','主机组','OpenShift版本','部署脚本']
    search_fields = ['hostname','address','version']

class FiletypeInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["模板类型"]
    search_fields = ('name')

class LogsAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["字段名"]

class SettingsAdmin(BaseAdmin):
    list_display = ("name","ipaddress","ports","model","ca_ert")
    list_filter = ["名称",'IP','端口','HTTP协议','证书']

site.register(models.Host,HostInfoAdmin)
site.register(models.Group,GroupInfoAdmin)
site.register(models.Version,VersionInfoAdmin)
site.register(models.Files,FilesInfoAdmin)
site.register(models.FileType,FiletypeInfoAdmin)
site.register(models.DeployList,DeplayLogsInfoAdmin)
site.register(models.Logs,LogsAdmin)
site.register(models.Settings,SettingsAdmin)



