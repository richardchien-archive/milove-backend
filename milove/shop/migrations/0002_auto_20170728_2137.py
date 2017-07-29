# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 13:37
from __future__ import unicode_literals

import django.contrib.auth.password_validation
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email address already exists.'}, max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, validators=[django.contrib.auth.password_validation.validate_password], verbose_name='password'),
        ),
    ]