#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models


class Group(models.Model):
    group_name = models.CharField(max_length=100,unique=True)

    class Meta:
        verbose_name = "主机组"
        verbose_name_plural = "主机组"

    def __str__(self):
        return self.group_name



class Version(models.Model):
    version_name = models.CharField(max_length=100,unique=True)

    class Meta:
        verbose_name = "OpenShift版本"
        verbose_name_plural = "OpenShift版本"

    def __str__(self):
        return self.version_name

class FileType(models.Model):
    name = models.CharField(max_length=128,unique=True)

    class Meta:
        verbose_name = "文件类型"
        verbose_name_plural = "文件类型"

    def __str__(self):
        return self.name

class LogsField(models.Model):
    name = models.CharField(max_length=128,unique=True)

    class Meta:
        verbose_name = "日志字段"
        verbose_name_plural = "日志字段"

    def __str__(self):
        return "%s" %self.name

class DeployList(models.Model):
    name = models.CharField(max_length=128)
    class Meta:
        verbose_name = '部署日志'
        verbose_name_plural = '部署日志'



class Files(models.Model):
    file_name = models.CharField(max_length=100)
    file_path = models.CharField(max_length=100)
    file_type = models.ForeignKey(FileType,related_name='files', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "部署脚本"
        verbose_name_plural = "部署脚本"

    def __str__(self):
        return self.file_name

class Host(models.Model):
    group = models.ForeignKey(Group, related_name='host', on_delete=models.CASCADE,blank=True,null=True)
    version = models.ForeignKey(Version, related_name='host', on_delete=models.CASCADE,blank=True,null=True)
    script = models.ForeignKey(Files, related_name='host', on_delete=models.CASCADE,blank=True,null=True)
    hostname = models.CharField(max_length=100)
    ipaddress = models.GenericIPAddressField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    port = models.IntegerField()

    class Meta:
        # unique_together = 'order'
        ordering = ['group','version','script']
        verbose_name = '主机列表'
        verbose_name_plural = '主机列表'

    def __unicode__(self):
        return '%s' % (self.port)

class Settings(models.Model):
    NAME_Choices=((0,'RabbitMQ'),(1,'ETCD'))
    name = models.SmallIntegerField(choices=NAME_Choices)
    ipaddress = models.GenericIPAddressField()
    ports = models.IntegerField(default=2379)
    Choices = ((0, 'http'), (1, 'https'))
    model = models.SmallIntegerField(choices=Choices)

    class Meta:
        verbose_name = "系统配置信息"
        verbose_name_plural = "系统配置信息"
