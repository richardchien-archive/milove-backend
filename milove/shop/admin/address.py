from django.contrib import admin

from ..admin_filters import AllValuesFieldDropdownFilter
from ..models.address import *


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'phone_number', 'country',
                    'province', 'city', 'zip_code')
    list_display_links = ('user', 'fullname')
    list_filter = (
        'country',
        ('province', AllValuesFieldDropdownFilter),
        ('city', AllValuesFieldDropdownFilter),
    )
    search_fields = ('user__username', 'fullname', 'street_address',
                     'phone_number', 'province', 'city', 'zip_code')


admin.site.register(Address, AddressAdmin)
