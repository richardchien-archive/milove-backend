from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings

from .product import Product


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


class Order(models.Model):
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             related_name='orders',
                             on_delete=models.SET_NULL, verbose_name=_('user'))
    total_price = models.FloatField(verbose_name=_('total price'))

    STATUS_UNPAID = 'unpaid'
    STATUS_PAID = 'paid'
    STATUS_SHIPPING = 'shipping'
    STATUS_DONE = 'done'
    STATUS_CANCELED = 'canceled'

    STATUSES = (
        (STATUS_UNPAID, _('OrderStatus|unpaid')),
        (STATUS_PAID, _('OrderStatus|paid')),
        (STATUS_SHIPPING, _('OrderStatus|shipping')),
        (STATUS_DONE, _('OrderStatus|done')),
        (STATUS_CANCELED, _('OrderStatus|canceled')),
    )

    status = models.CharField(max_length=20, choices=STATUSES,
                              default=STATUS_UNPAID,
                              verbose_name=_('status'))

    PAYMENT_BALANCE = 'balance'
    PAYMENT_PAYPAL = 'paypal'
    PAYMENT_STRIPE = 'stripe'

    PAYMENT_METHODS = (
        (PAYMENT_BALANCE, _('PaymentMethod|balance')),
        (PAYMENT_PAYPAL, _('PaymentMethod|paypal')),
        (PAYMENT_STRIPE, _('PaymentMethod|stripe')),
    )

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS,
                                      verbose_name=_('payment method'))
    use_balance = models.BooleanField(verbose_name=_('Order|use balance'))
    from_balance = models.FloatField(
        verbose_name=_('Order|from balance'))  # money paid from balance

    # transaction id for 3rd party payment methods
    # transaction_id = models.CharField(max_length=200, verbose_name=_('transaction id'))

    def __str__(self):
        return 'Order #{}'.format(self.id)


@receiver(signals.pre_save, sender=Order)
def handle(instance, **_):
    if instance.status == Order.STATUS_CANCELED:
        # cancel an order
        with transaction.atomic():
            for item in instance.items.all():
                item.product.sold = False
                item.product.save()
