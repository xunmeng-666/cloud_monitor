# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-08-31 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Adeployment', '0002_auto_20180831_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logsfield',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
