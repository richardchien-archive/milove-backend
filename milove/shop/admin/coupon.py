from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from ..models.coupon import *


class CouponAdmin(admin.ModelAdmin):
    def get_discount(self, instance):
        if instance.type == Coupon.TYPE_RATE:
            return '-%s%%' % instance.discount
        else:
            return '-$%s' % instance.discount

    get_discount.short_description = _('Coupon|discount')
    get_discount.admin_order_field = 'discount'

    list_display = ('code', 'type', 'price_required',
                    'get_discount', 'is_valid')
    list_filter = ('type', 'is_valid')
    list_editable = ('is_valid',)


admin.site.register(Coupon, CouponAdmin)
