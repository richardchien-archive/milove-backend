from django.contrib import admin

from milove.shop.models import *


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)


class ProductAdmin(admin.ModelAdmin):
    fields = ('sold',
              'brand', 'name', 'size', 'style', 'condition', 'categories', 'attachments',
              'description', 'original_price', 'price', 'main_image', 'main_image_preview',)
    readonly_fields = ('main_image_preview',)
    list_display = ('main_image_preview', 'brand', 'name', 'size', 'style',
                    'condition', 'categories_string', 'original_price', 'price', 'sold')
    list_filter = ('brand', 'condition', 'sold')
    search_fields = ('brand__name', 'name', 'style')
    inlines = (ProductImageInline,)


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
