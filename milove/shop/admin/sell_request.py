from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from django.core import exceptions

from ..models.sell_request import *


class SellRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'brand', 'category', 'name', 'size',
                    'condition', 'year', 'original_price')
    list_display_links = ('id', 'user', 'brand')
    ordering = ('-created_dt',)
    search_fields = ('id', 'user__username', 'user__email',
                     'brand', 'category', 'name', 'description')

    fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
              'size', 'condition', 'year', 'original_price', 'attachments',
              'description', 'buy_back_price', 'sell_price')
    readonly_fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
                       'size', 'condition', 'year', 'original_price',
                       'attachments', 'description')


admin.site.register(SellRequest, SellRequestAdmin)
