# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-08 01:55
from __future__ import unicode_literals

from django.db import migrations, models
import milove.shop.models.sell_request


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_sellrequest_shipping_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellrequest',
            name='express_company',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='express company'),
        ),
        migrations.AddField(
            model_name='sellrequest',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='tracking number'),
        ),
        migrations.AlterField(
            model_name='sellrequest',
            name='shipping_label',
            field=models.FileField(blank=True, null=True, upload_to=milove.shop.models.sell_request._shipping_label_upload_path, verbose_name='shipping label'),
        ),
    ]
