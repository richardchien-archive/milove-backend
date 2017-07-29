# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20170729_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='name',
            field=models.CharField(default=1, max_length=200, verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='method',
            field=models.CharField(choices=[('credit-card', 'credit card')], max_length=20, verbose_name='PaymentMethod|method'),
        ),
    ]
