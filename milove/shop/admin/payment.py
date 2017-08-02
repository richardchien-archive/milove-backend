from django.contrib import admin

from ..models.payment import *


class BillingAddressInline(admin.StackedInline):
    model = BillingAddress

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'amount_from_balance',
                    'amount_from_point', 'method', 'vendor_payment_id',
                    'status')
    list_display_links = ('id', 'order')
    list_filter = ('method', 'status',)
    inlines = (BillingAddressInline,)
    ordering = ('-created_dt',)
    search_fields = ('id', 'order__user__username', 'order__user__email',
                     'method', 'vendor_payment_id')

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


admin.site.register(Payment, PaymentAdmin)
