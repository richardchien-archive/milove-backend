# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 06:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_auto_20170731_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Order|comment'),
        ),
    ]