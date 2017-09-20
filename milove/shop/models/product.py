import os
import hashlib

from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ..model_utils import get_or_none
from ..file_storage import storage

__all__ = ['Brand', 'Category', 'Attachment',
           'AuthenticationMethod', 'ProductLocation',
           'ProductImage', 'Product']


class Brand(models.Model):
    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    name = models.CharField(_('name'), max_length=200, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    name = models.CharField(_('name'), max_length=50)
    super_category = models.ForeignKey('self', related_name='children',
                                       blank=True, null=True,
                                       on_delete=models.CASCADE,
                                       verbose_name=_('super category'))
    level = models.IntegerField(_('category level'), editable=False)

    def __str__(self):
        if not self.super_category:
            return self.name
        return str(self.super_category) + ' - ' + str(self.name)

    def simple_name(self):
        simple_name = self.name
        if self.super_category:
            cat = self.super_category
            while cat.super_category:
                cat = cat.super_category
            # now "cat" is the most top level category
            simple_name = cat.name + simple_name
        return simple_name


@receiver(signals.pre_save, sender=Category)
def category_pre_save(sender, instance: Category, **kwargs):
    level = 1
    cat = instance
    while cat.super_category:
        level += 1
        cat = cat.super_category
    instance.level = level


class Attachment(models.Model):
    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')

    name = models.CharField(_('name'), max_length=50, unique=True)

    def __str__(self):
        return self.name


class AuthenticationMethod(models.Model):
    class Meta:
        verbose_name = _('authentication method')
        verbose_name_plural = _('authentication methods')

    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProductLocation(models.Model):
    class Meta:
        verbose_name = _('product location')
        verbose_name_plural = _('product locations')

    name = models.CharField(_('name'), max_length=200, unique=True)

    def __str__(self):
        return self.name


def _prod_image_path(_, filename):
    filename, ext = os.path.splitext(filename)
    now = timezone.now()
    filename_hash = hashlib.md5()
    filename_hash.update(filename.encode('utf-8'))
    filename_hash.update(str(now.timestamp()).encode('utf-8'))
    return 'uploads/{}-{}{}'.format(now.strftime('%Y%m%d%H%M%S'),
                                    filename_hash.hexdigest(), ext)


_prod_image_placeholder_path = 'placeholders/120x120.png'


class ProductImage(models.Model):
    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    image = models.ImageField(_('image'), upload_to=_prod_image_path)
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='images',
                                verbose_name=_('product'))

    def __str__(self):
        return self.image.name


class Product(models.Model):
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    published_dt = models.DateTimeField(_('Product|published datetime'),
                                        auto_now_add=True)

    show_on_homepage = models.BooleanField(_('Product|show on homepage'),
                                           default=False)

    sold = models.BooleanField(_('Product|sold'), default=False)
    sold_dt = models.DateTimeField(_('Product|sold datetime'),
                                   null=True, blank=True)

    @staticmethod
    def sold_changed(_, new_obj):
        if new_obj.sold is True:
            new_obj.sold_dt = timezone.now()
        else:
            new_obj.sold_dt = None

    brand = models.ForeignKey('Brand', on_delete=models.CASCADE,
                              related_name='products',
                              verbose_name=_('Product|brand'))
    name = models.CharField(_('Product|name'),
                            help_text=_('Name of the product.'),
                            max_length=200, blank=True)
    style = models.CharField(_('Product|style'),
                             help_text=_('Style of the product.'),
                             max_length=200, blank=True)
    color = models.CharField(_('Product|color'),
                             help_text=_('Color of the product.'),
                             max_length=200, blank=True)
    size = models.CharField(_('Product|size'),
                            help_text=_('Size of the product.'),
                            max_length=20, blank=True)

    CONDITION_S = 'S'
    CONDITION_A_PLUS = 'A+'
    CONDITION_A = 'A'
    CONDITION_B = 'B'
    CONDITION_C = 'C'
    CONDITION_D = 'D'

    CONDITIONS = (
        (CONDITION_S, _('ProductCondition|S')),
        (CONDITION_A_PLUS, _('ProductCondition|A+')),
        (CONDITION_A, _('ProductCondition|A')),
        (CONDITION_B, _('ProductCondition|B')),
        (CONDITION_C, _('ProductCondition|C')),
        (CONDITION_D, _('ProductCondition|D')),
    )

    condition = models.CharField(_('Product|condition'),
                                 max_length=2, choices=CONDITIONS)

    categories = models.ManyToManyField('Category', blank=True,
                                        related_name='products',
                                        verbose_name=_('Product|categories'))
    attachments = models.ManyToManyField('Attachment', blank=True,
                                         verbose_name=_('Product|attachments'))
    description = models.TextField(_('Product|description'), blank=True)
    serial_code = models.CharField(_('Product|serial code'),
                                   max_length=200, blank=True)
    authentication_methods = models.ManyToManyField(
        'AuthenticationMethod', related_name='products', blank=True,
        verbose_name=_('Product|authentication methods'))
    location = models.ForeignKey('ProductLocation', related_name='products',
                                 null=True, blank=True,
                                 verbose_name=_('Product|location'))
    purchase_year = models.IntegerField(_('Product|purchase year'),
                                        blank=True, null=True)
    original_price = models.FloatField(_('Product|original price'))
    buy_back_price = models.FloatField(_('Product|buy back price'),
                                       help_text=_('Customers won\'t '
                                                   'see this price.'),
                                       null=True, blank=True)
    price = models.FloatField(_('Product|price'))

    main_image = models.ImageField(_('Product|main image'),
                                   default=_prod_image_placeholder_path,
                                   upload_to=_prod_image_path)

    def __str__(self):
        return ('#%s ' % self.pk) + self.brand.name \
               + (' ' + self.name if self.name else '')


@receiver(signals.pre_save, sender=Product)
def product_pre_save(sender, instance: Product, **kwargs):
    old = get_or_none(sender, pk=instance.pk)
    if old is None or old.sold != instance.sold:
        instance.sold_changed(old, instance)


def _move_image_if_needed(product_id, name):
    if name.startswith('uploads/') and storage.exists(name):
        pure_name = name.split('/')[-1]
        new_dir = 'products/%s/' % product_id
        os.makedirs(storage.path(new_dir), exist_ok=True)
        new_name = new_dir + pure_name
        os.rename(storage.path(name), storage.path(new_name))
        return new_name


@receiver(signals.post_save, sender=Product)
def product_post_save(instance: Product, **kwargs):
    new_main_image_name = _move_image_if_needed(instance.pk,
                                                instance.main_image.name)
    if new_main_image_name:
        instance.main_image = new_main_image_name
        instance.save()


@receiver(signals.post_save, sender=ProductImage)
def product_image_post_save(instance: ProductImage, **kwargs):
    new_image_name = _move_image_if_needed(instance.product.pk,
                                           instance.image.name)
    if new_image_name:
        instance.image = new_image_name
        instance.save()


@receiver(signals.m2m_changed, sender=Product.categories.through)
def product_categories_changed(instance, action, **kwargs):
    if action not in ('post_add', 'post_remove'):
        return

    # include all possible super categories
    categories_set = set(instance.categories.all())
    old_set = categories_set.copy()
    for cat in instance.categories.all():
        while cat.super_category:
            categories_set.add(cat.super_category)
            cat = cat.super_category
    if categories_set != old_set:
        instance.categories = categories_set
