# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 04:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_auto_20170801_0923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': (('randomly_switch_order_status', 'Can randomly switch order status'),), 'verbose_name': 'order', 'verbose_name_plural': 'orders'},
        ),
    ]