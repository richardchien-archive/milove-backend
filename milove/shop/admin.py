from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *

admin.site.site_header = admin.site.site_title = _('Milove Admin')


# Admin of goods

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ('image', 'get_image_preview')
    readonly_fields = ('get_image_preview',)


class ProductAdmin(admin.ModelAdmin):
    fields = ('sold',
              'brand', 'name', 'size', 'style', 'condition', 'categories', 'attachments',
              'description', 'original_price', 'price', 'main_image', 'get_main_image_preview',)
    readonly_fields = ('get_main_image_preview',)
    list_display = ('id', 'get_main_image_preview', 'brand', 'name', 'size', 'style',
                    'condition', 'categories_string', 'original_price', 'price', 'sold')
    list_display_links = ('id', 'get_main_image_preview')
    ordering = ('id',)
    list_filter = ('brand', 'condition', 'sold')
    search_fields = ('brand__name', 'name', 'style')
    inlines = (ProductImageInline,)


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)


# Admin of users

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'get_username', 'get_email', 'nickname', 'balance', 'point')
    list_display_links = ('get_id', 'get_username')
    ordering = ('user__id',)


class UserInfoInline(admin.StackedInline):
    model = UserInfo


UserAdmin.inlines = (UserInfoInline,)
UserAdmin.list_display = ('id',) + UserAdmin.list_display
UserAdmin.list_display_links = ('id', 'username')
UserAdmin.ordering = ('id',)

admin.site.register(UserInfo, UserInfoAdmin)


# Admin of orders

class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'price')
    readonly_fields = ('product',)
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'use_balance', 'from_balance', 'payment_method', 'status')
    list_filter = ('status', 'payment_method')
    fields = ('user', 'total_price', 'status', 'payment_method', 'use_balance', 'from_balance')
    readonly_fields = ('user', 'total_price', 'use_balance', 'from_balance')
    inlines = (OrderItemAdmin,)
    ordering = ('id',)


admin.site.register(Order, OrderAdmin)
