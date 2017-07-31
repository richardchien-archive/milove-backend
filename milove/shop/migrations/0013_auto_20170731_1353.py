# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 05:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_order_discount_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='discount_amount',
            field=models.FloatField(blank=True, default=0.0, verbose_name='discount amount'),
        ),
    ]