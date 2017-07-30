from django.contrib import admin

from ..models.order import *


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'price')
    readonly_fields = ('product',)
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    # list_display = ('id', 'user', 'total_price', 'use_balance', 'from_balance',
    #                 'payment_method', 'status')
    # list_filter = ('status', 'payment_method')
    # fields = ('user', 'total_price', 'status', 'payment_method', 'use_balance',
    #           'from_balance')
    # readonly_fields = ('user', 'total_price', 'use_balance', 'from_balance')
    inlines = (OrderItemInline, ShippingAddressInline)
    ordering = ('-created_dt',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatusTransition)
