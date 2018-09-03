# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-08-31 10:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeployList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u90e8\u7f72\u65e5\u5fd7',
                'verbose_name_plural': '\u90e8\u7f72\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=100)),
                ('file_path', models.CharField(max_length=100)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u90e8\u7f72\u811a\u672c',
                'verbose_name_plural': '\u90e8\u7f72\u811a\u672c',
            },
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'verbose_name': '\u6587\u4ef6\u7c7b\u578b',
                'verbose_name_plural': '\u6587\u4ef6\u7c7b\u578b',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': '\u4e3b\u673a\u7ec4',
                'verbose_name_plural': '\u4e3b\u673a\u7ec4',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=100)),
                ('ipaddress', models.GenericIPAddressField()),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('port', models.IntegerField()),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host', to='Adeployment.Group')),
                ('script', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host', to='Adeployment.Files')),
            ],
            options={
                'ordering': ['group', 'version', 'script'],
                'verbose_name': '\u4e3b\u673a\u5217\u8868',
                'verbose_name_plural': '\u4e3b\u673a\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='LogsField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'verbose_name': '\u65e5\u5fd7\u5b57\u6bb5',
                'verbose_name_plural': '\u65e5\u5fd7\u5b57\u6bb5',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SmallIntegerField(choices=[(0, b'RabbitMQ'), (1, b'ETCD')])),
                ('ipaddress', models.GenericIPAddressField()),
                ('ports', models.IntegerField(default=2379)),
                ('model', models.SmallIntegerField(choices=[(0, b'http'), (1, b'https')])),
            ],
            options={
                'verbose_name': '\u7cfb\u7edf\u914d\u7f6e\u4fe1\u606f',
                'verbose_name_plural': '\u7cfb\u7edf\u914d\u7f6e\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'OpenShift\u7248\u672c',
                'verbose_name_plural': 'OpenShift\u7248\u672c',
            },
        ),
        migrations.AddField(
            model_name='host',
            name='version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host', to='Adeployment.Version'),
        ),
        migrations.AddField(
            model_name='files',
            name='file_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='Adeployment.FileType'),
        ),
    ]
