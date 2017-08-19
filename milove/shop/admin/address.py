from django.contrib import admin

from ..admin_filters import AllValueFieldDropdownFilter
from ..models.address import *


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'phone_number', 'country',
                    'province', 'city', 'zip_code')
    list_display_links = ('user', 'fullname')
    list_filter = (
        'country',
        ('province', AllValueFieldDropdownFilter),
        ('city', AllValueFieldDropdownFilter),
    )
    search_fields = ('user__username', 'fullname', 'street_address',
                     'phone_number', 'province', 'city', 'zip_code')


# TODO: 生产环境这里不要加
admin.site.register(Address, AddressAdmin)
