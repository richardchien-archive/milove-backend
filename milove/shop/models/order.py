from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings

from .product import Product
from .address import AbstractAddress

__all__ = ['OrderItem', 'ShippingAddress', 'Order', 'OrderStatusTransition']


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

    # basic information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             related_name='orders',
                             on_delete=models.SET_NULL, verbose_name=_('user'))
    total_price = models.FloatField(_('total price'))
    discount_amount = models.FloatField(_('discount amount'), default=0.0,
                                        blank=True)
    created_dt = models.DateTimeField(_('created datetime'), auto_now_add=True)
    comment = models.TextField(_('Order|comment'), blank=True)

    STATUS_UNPAID = 'unpaid'
    STATUS_PAID = 'paid'
    STATUS_SHIPPING = 'shipping'
    STATUS_DONE = 'done'
    STATUS_CANCELLING = 'cancelling'
    STATUS_CANCELLED = 'cancelled'
    STATUS_RETURN_REQUESTED = 'return-requested'
    STATUS_RETURNING = 'returning'
    STATUS_RETURNED = 'returned'

    STATUSES = (
        (STATUS_UNPAID, _('OrderStatus|unpaid')),
        (STATUS_PAID, _('OrderStatus|paid')),
        (STATUS_SHIPPING, _('OrderStatus|shipping')),
        (STATUS_DONE, _('OrderStatus|done')),
        (STATUS_CANCELLING, _('OrderStatus|cancelling')),
        (STATUS_CANCELLED, _('OrderStatus|cancelled')),
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
        return _('Order #%(id)s') % {'id': self.id}


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

# @receiver(signals.pre_save, sender=Order)
# def handle(instance, **_):
#     if instance.status == Order.STATUS_CANCELED:
#         # cancel an order
#         with transaction.atomic():
#             for item in instance.items.all():
#                 item.product.sold = False
#                 item.product.save()
