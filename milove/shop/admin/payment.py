from django.contrib import admin

from ..models.payment import *


class BillingAddressInline(admin.StackedInline):
    model = BillingAddress

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'type', 'amount_from_balance',
                    'amount_from_point', 'method', 'vendor_payment_id',
                    'status')
    list_display_links = ('id', 'order')
    list_filter = ('type', 'method', 'status',)
    inlines = (BillingAddressInline,)
    ordering = ('-created_dt',)
    search_fields = ('id', 'order__user__username', 'order__user__email',
                     'method', 'vendor_payment_id')

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        # only users can create payments
        if request.user.is_superuser:
            # except superuser
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # no one can delete payments
        if request.user.is_superuser:
            # except superuser
            return True
        return False


admin.site.register(Payment, PaymentAdmin)
