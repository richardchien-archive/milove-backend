from django.contrib import admin

from ..admin_filters import AllValueFieldDropdownFilter
from ..models.payment import *


class PaymentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Payment, PaymentAdmin)
