from django.contrib import admin

from ..models.order import *


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'price')
    readonly_fields = ('product', 'price')  # order item should not be edited
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
    list_display = ('id', 'user', 'total_price', 'discount_amount',
                    'comment', 'status', 'tracking_number')
    list_display_links = ('id', 'user')
    list_filter = ('status',)
    inlines = (OrderItemInline, ShippingAddressInline)
    ordering = ('-created_dt',)
    search_fields = ('id', 'user__username', 'comment', 'tracking_number')

    fields = ('user', 'total_price', 'discount_amount', 'comment',
              'status', 'last_status',
              'express_company', 'tracking_number')
    readonly_fields = ('user', 'total_price', 'comment', 'last_status')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatusTransition)
