from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db import models as db_models
from django import forms

from ..admin_filters import RelatedFieldDropdownFilter, \
    ChoicesFieldDropdownFilter
from ..models.product import *


class _ModelWithProductCount(admin.ModelAdmin):
    """Base model for models that have products relationship

    This base class adds 'product_count', 'product_for_sale_count' annotations,
    and 'get_product_count', 'get_product_for_sale_count' methods,
    to subclasses.

    The subclasses MUST have 'products' relation,
    which means there is a ForeignKey or other relation field
    referring to the model, and the field's 'relation_name' is 'products'.
    """

    def get_queryset(self, request):
        # https://stackoverflow.com/questions/30752268/how-to-filter-objects-for-count-annotation-in-django
        return super().get_queryset(request).annotate(
            product_count=db_models.Count('products'),
            product_for_sale_count=db_models.Sum(db_models.Case(
                db_models.When(products__sold=False, then=1),
                default=0,
                output_field=db_models.IntegerField()
            )),
        )

    def get_product_count(self, instance: Brand):
        return getattr(instance, 'product_count')

    get_product_count.short_description = _('total number of products')
    get_product_count.admin_order_field = 'product_count'

    def get_product_for_sale_count(self, instance: Brand):
        return getattr(instance, 'product_for_sale_count')

    get_product_for_sale_count.short_description \
        = _('number of products for sale')
    get_product_for_sale_count.admin_order_field = 'product_for_sale_count'


class BrandAdmin(_ModelWithProductCount):
    list_display = ('id', 'name', 'get_product_count',
                    'get_product_for_sale_count')
    list_display_links = ('id', 'name')
    ordering = ('id',)
    search_fields = ('name',)


admin.site.register(Brand, BrandAdmin)


class CategoryAdmin(_ModelWithProductCount):
    list_display = ('id', 'name', 'super_category', 'get_product_count',
                    'get_product_for_sale_count')
    list_display_links = ('id', 'name')
    ordering = ('id',)


admin.site.register(Category, CategoryAdmin)

admin.site.register(Attachment)


class ProductImageInline(admin.TabularInline):
    model = ProductImage

    def get_image_preview(self, instance: ProductImage):
        if instance.image_thumb:
            return '<img src="%s" width="120" />' % instance.image_thumb.url
        return '-'

    get_image_preview.short_description = _('image preview')
    get_image_preview.allow_tags = True

    fields = ('image', 'get_image_preview')
    readonly_fields = ('get_image_preview',)


class ProductAdmin(admin.ModelAdmin):
    def get_main_image_preview(self, instance: Product):
        if instance.main_image_thumb:
            return '<img src="%s" width="120" />' \
                   % instance.main_image_thumb.url
        return '-'

    get_main_image_preview.short_description = _('Product|main image preview')
    get_main_image_preview.allow_tags = True

    def get_categories_string(self, instance: Product):
        return ', '.join(map(str, instance.categories.all()))

    get_categories_string.short_description = _('Product|categories')

    def get_price_fraction(self, instance: Product):
        return '{} / {}'.format(instance.price, instance.original_price)

    get_price_fraction.short_description = _('Product|price / original price')
    get_price_fraction.admin_order_field = 'price'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'brand':
            # sort the brand dropdown
            kwargs['queryset'] = Brand.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_per_page = 20
    list_max_show_all = 100
    list_display = ('id', 'get_main_image_preview',
                    'brand', 'name', 'style', 'size', 'condition',
                    'get_categories_string', 'get_price_fraction',
                    'buy_back_price', 'sold')
    list_display_links = ('id', 'get_main_image_preview')
    ordering = ('-publish_dt',)  # order by publish datetime descending
    list_editable = ('sold',)
    list_filter = (
        'publish_dt', 'sold', 'sold_dt',
        ('brand', RelatedFieldDropdownFilter),
        ('condition', ChoicesFieldDropdownFilter),
        ('categories', RelatedFieldDropdownFilter),
        ('attachments', RelatedFieldDropdownFilter)
    )
    search_fields = ('id', 'brand__name', 'name', 'style',
                     'size', 'description')

    fields = ('publish_dt', 'sold', 'sold_dt', 'brand', 'name', 'style',
              'size', 'condition', 'categories', 'attachments', 'description',
              'original_price', 'buy_back_price', 'price',
              'main_image', 'get_main_image_preview')
    readonly_fields = ('publish_dt', 'sold_dt', 'get_main_image_preview',)
    inlines = (ProductImageInline,)

    # filter_horizontal = ('categories', 'attachments')

    class Form(forms.ModelForm):
        class AjaxImageField(forms.CharField):
            widget = forms.TextInput

        # main_image = AjaxImageField(label=_('Product|main image'))
        # TODO: this should be customized
        # see https://github.com/bradleyg/django-ajaximage

        class Meta:
            model = Product
            fields = '__all__'

    form = Form


admin.site.register(Product, ProductAdmin)
