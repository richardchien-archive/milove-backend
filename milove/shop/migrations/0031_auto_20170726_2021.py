# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0030_auto_20170726_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='publish_dt',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Product|publish datetime'),
        ),
    ]
