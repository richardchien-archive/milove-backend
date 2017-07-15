from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


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
    list_display = ('get_main_image_preview', 'brand', 'name', 'size', 'style',
                    'condition', 'categories_string', 'original_price', 'price', 'sold')
    list_filter = ('brand', 'condition', 'sold')
    search_fields = ('brand__name', 'name', 'style')
    inlines = (ProductImageInline,)


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)


# Admin of user

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'get_username', 'get_email', 'nickname', 'balance', 'point')
    ordering = ('user__id', 'user__username')


class UserInfoInline(admin.StackedInline):
    model = UserInfo


UserAdmin.inlines = [UserInfoInline]
UserAdmin.list_display = ('id',) + UserAdmin.list_display
UserAdmin.ordering = ('id', 'username')

admin.site.register(UserInfo, UserInfoAdmin)
