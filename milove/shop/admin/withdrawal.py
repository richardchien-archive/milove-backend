from django.contrib import admin

from ..models.withdrawal import *


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'processed_amount',
                    'method', 'vendor_account', 'status')
    list_display_links = ('id', 'user')
    list_filter = ('method', 'status',)
    ordering = ('-created_dt',)
    search_fields = ('id', 'user__username', 'user__email',
                     'method', 'vendor_account')

    fields = ('id', 'created_dt', 'user', 'amount', 'processed_amount',
              'method', 'vendor_account', 'status')
    readonly_fields = ('id', 'created_dt', 'user', 'amount')

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


admin.site.register(Withdrawal, WithdrawalAdmin)
