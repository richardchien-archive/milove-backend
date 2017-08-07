import functools

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings

from .product import Product
from .address import AbstractAddress
from .helpers import *
from .. import mail_shortcuts as mail

__all__ = ['OrderItem', 'ShippingAddress', 'Order', 'OrderStatusTransition',
           'get_direct_src_statuses', 'get_direct_dst_statuses',
           'is_status_transition_allowed']


class OrderItem(models.Model):
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    product = models.ForeignKey(Product, on_delete=models.PROTECT,
                                verbose_name=_('product'))
    order = models.ForeignKey('Order', related_name='items',
                              on_delete=models.CASCADE,
                              verbose_name=_('order'))
    price = models.FloatField(verbose_name=_('strike price'))

    def get_product_main_image_preview(self):
        if self.product.main_image_thumb:
            return '<img src="%s" width="120" />' \
                   % self.product.main_image_thumb.url
        return '-'

    get_product_main_image_preview.short_description = _(
        'Product|main image preview')
    get_product_main_image_preview.allow_tags = True

    def __str__(self):
        return str(self.product)


class ShippingAddress(AbstractAddress):
    class Meta:
        verbose_name = _('shipping address')
        verbose_name_plural = _('shipping addresses')

    order = models.OneToOneField('Order', on_delete=models.CASCADE,
                                 related_name='shipping_address',
                                 verbose_name=_('order'))


class Order(models.Model):
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        permissions = (
            ('randomly_switch_order_status',
             'Can randomly switch order status'),
        )

    # basic information
    created_dt = models.DateTimeField(_('created datetime'), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             related_name='orders',
                             on_delete=models.SET_NULL, verbose_name=_('user'))
    total_price = models.FloatField(_('total price'))
    discount_amount = models.FloatField(_('discount amount'), default=0.0,
                                        blank=True)
    paid_amount = models.FloatField(_('paid amount'), default=0.0, blank=True)
    comment = models.TextField(_('Order|comment'), blank=True)

    STATUS_UNPAID = 'unpaid'
    STATUS_CLOSED = 'closed'
    STATUS_PAID = 'paid'
    STATUS_CANCELLING = 'cancelling'
    STATUS_CANCELLED = 'cancelled'
    STATUS_SHIPPING = 'shipping'
    STATUS_DONE = 'done'
    STATUS_RETURN_REQUESTED = 'return-requested'
    STATUS_RETURNING = 'returning'
    STATUS_RETURNED = 'returned'

    STATUSES = (
        (STATUS_UNPAID, _('OrderStatus|unpaid')),
        (STATUS_CLOSED, _('OrderStatus|closed')),
        (STATUS_PAID, _('OrderStatus|paid')),
        (STATUS_CANCELLING, _('OrderStatus|cancelling')),
        (STATUS_CANCELLED, _('OrderStatus|cancelled')),
        (STATUS_SHIPPING, _('OrderStatus|shipping')),
        (STATUS_DONE, _('OrderStatus|done')),
        (STATUS_RETURN_REQUESTED, _('OrderStatus|return requested')),
        (STATUS_RETURNING, _('OrderStatus|returning')),
        (STATUS_RETURNED, _('OrderStatus|returned')),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUSES,
                              default=STATUS_UNPAID)
    last_status = models.CharField(_('last status'), max_length=20,
                                   choices=STATUSES, null=True, blank=True)

    # shipping information
    express_company = models.CharField(_('express company'),
                                       null=True, blank=True, max_length=60)
    tracking_number = models.CharField(_('tracking number'),
                                       null=True, blank=True, max_length=30)

    def __str__(self):
        return _('Order #%(pk)s') % {'pk': self.pk}

    @staticmethod
    def status_changed(old_obj, new_obj):
        # log status changes
        new_obj.last_status = old_obj.status
        OrderStatusTransition.objects.create(
            order=new_obj,
            src_status=new_obj.last_status,
            dst_status=new_obj.status
        )

        if new_obj.status in (Order.STATUS_CLOSED,
                              Order.STATUS_CANCELLED):
            # close or cancel an order, restore all products related
            with transaction.atomic():
                for item in new_obj.items.all():
                    item.product.sold = False
                    item.product.save()
        if new_obj.status == Order.STATUS_DONE:
            # the order is done, give the user some points
            new_obj.user.info.point += settings.AMOUNT_TO_POINT(
                new_obj.paid_amount
            )
            new_obj.user.info.save()


class OrderStatusTransition(models.Model):
    class Meta:
        verbose_name = _('order status transition')
        verbose_name_plural = _('order status transitions')

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='status_transitions',
                              verbose_name=_('order'))
    happened_dt = models.DateTimeField(_('happened datetime'),
                                       auto_now_add=True)
    src_status = models.CharField(_('source status'), max_length=20,
                                  choices=Order.STATUSES)
    dst_status = models.CharField(_('destination status'), max_length=20,
                                  choices=Order.STATUSES)


@receiver(signals.pre_save, sender=Order)
def order_pre_save(instance, **kwargs):
    old_instance = None
    if instance.pk:
        old_instance = Order.objects.get(pk=instance.pk)

    if old_instance and old_instance.status != instance.status:
        instance.status_changed(old_instance, instance)

        # notify related user and staffs
        mail.notify_order_status_changed(instance)


_STATUS_SIDES = (
    (Order.STATUS_UNPAID, Order.STATUS_CANCELLED),
    (Order.STATUS_UNPAID, Order.STATUS_CLOSED),
    (Order.STATUS_UNPAID, Order.STATUS_PAID),
    (Order.STATUS_PAID, Order.STATUS_CANCELLING),
    (Order.STATUS_PAID, Order.STATUS_CANCELLED),
    (Order.STATUS_PAID, Order.STATUS_SHIPPING),
    (Order.STATUS_CANCELLING, Order.STATUS_CANCELLED),
    (Order.STATUS_SHIPPING, Order.STATUS_DONE),
    (Order.STATUS_DONE, Order.STATUS_RETURN_REQUESTED),
    (Order.STATUS_RETURN_REQUESTED, Order.STATUS_DONE),
    (Order.STATUS_RETURN_REQUESTED, Order.STATUS_RETURNING),
    (Order.STATUS_RETURNING, Order.STATUS_RETURNED),
)

_STATUSES = dict(Order.STATUSES).keys()

get_direct_src_statuses = functools.partial(base_get_direct_src_statuses,
                                            _STATUSES, _STATUS_SIDES)
get_direct_dst_statuses = functools.partial(base_get_direct_dst_statuses,
                                            _STATUSES, _STATUS_SIDES)
is_status_transition_allowed = functools.partial(
    base_is_status_transition_allowed, _STATUSES, _STATUS_SIDES)
