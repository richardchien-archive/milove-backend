from django.db import models
from django.utils.translation import ugettext_lazy as _
from imagekit import ImageSpec
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Brand(models.Model):
    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    name = models.CharField(max_length=200, verbose_name=_('name'))

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    name = models.CharField(max_length=50, verbose_name=_('name'))
    super_category = models.ForeignKey('self', blank=True, null=True,
                                       on_delete=models.CASCADE, verbose_name=_('super category'))

    def __str__(self):
        if not self.super_category:
            return self.name
        return str(self.super_category) + ' - ' + str(self.name)


_prod_image_path = 'images/products/'


class _Thumbnail(ImageSpec):
    processors = [ResizeToFill(120, 120)]
    format = 'JPEG'
    options = {'quality': 80}


class Product(models.Model):
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                              related_name='products', verbose_name=_('Product|brand'))
    name = models.CharField(max_length=200, blank=True, verbose_name=_('Product|name'))
    size = models.CharField(max_length=20, blank=True, verbose_name=_('Product|size'))
    style = models.CharField(max_length=200, verbose_name=_('Product|style'))
    condition = models.CharField(max_length=20, verbose_name=_('Product|condition'))
    categories = models.ManyToManyField(Category, related_name='products', verbose_name=_('Product|categories'))
    attachments = models.CharField(max_length=200, verbose_name=_('Product|attachments'))
    description = models.TextField(verbose_name=_('Product|description'))
    original_price = models.FloatField(verbose_name=_('Product|original price'))
    price = models.FloatField(verbose_name=_('Product|price'))
    sold = models.BooleanField(default=False, verbose_name=_('Product|sold'))

    main_image = models.ImageField(default='images/placeholder-120x120.png',
                                   upload_to=_prod_image_path, verbose_name=_('Product|main image'))
    main_image_thumb = ImageSpecField(source='main_image', spec=_Thumbnail)

    def get_main_image_preview(self):
        if self.main_image_thumb:
            return '<img src="%s" width="120" />' % self.main_image_thumb.url
        return '-'

    get_main_image_preview.short_description = _('Product|main image preview')
    get_main_image_preview.allow_tags = True

    def categories_string(self):
        return ', '.join(map(str, self.categories.all()))

    categories_string.short_description = _('Product|categories')

    def __str__(self):
        return '[{}] {}'.format(self.condition, self.brand) + (' ' + str(self.name) if self.name else '')


class ProductImage(models.Model):
    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    image = models.ImageField(upload_to=_prod_image_path, verbose_name=_('image'))
    image_thumb = ImageSpecField(source='image', spec=_Thumbnail)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))

    def get_image_preview(self):
        if self.image_thumb:
            return '<img src="%s" width="120" />' % self.image_thumb.url
        return '-'

    get_image_preview.short_description = _('image preview')
    get_image_preview.allow_tags = True

    def __str__(self):
        return str(self.image)
