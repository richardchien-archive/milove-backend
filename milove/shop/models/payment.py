from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from jsonfield import JSONField

from .payment_method import PaymentMethod
from .order import Order
from .address import AbstractAddress

__all__ = ['BillingAddress', 'Payment']


class BillingAddress(AbstractAddress):
    class Meta:
        verbose_name = _('billing address')
        verbose_name_plural = _('billing addresses')

    payment = models.OneToOneField('Payment', on_delete=models.CASCADE,
                                   related_name='billing_address',
                                   verbose_name=_('payment'))


class Payment(models.Model):
    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    created_dt = models.DateTimeField(_('created datetime'), auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='payments', verbose_name=_('order'))
    amount = models.FloatField(_('Payment|amount'))

    use_balance = models.BooleanField(_('Payment|use balance'))
    amount_from_balance = models.FloatField(_('Payment|amount from balance'),
                                            default=0.0)

    use_point = models.BooleanField(_('Payment|use point'))
    amount_from_point = models.FloatField(_('Payment|amount from point'),
                                          default=0.0)
    point_used = models.IntegerField(_('Payment|point used'), default=0)

    METHODS = (
        (PaymentMethod.PAYPAL, _('PayPal')),
        (PaymentMethod.CREDIT_CARD, _('credit card'))
    )

    method = models.CharField(_('Payment|method'), null=True, blank=True,
                              max_length=20, choices=METHODS)
    vendor_payment_id = models.CharField(_('Payment|vendor payment ID'),
                                         null=True, blank=True, max_length=100)
    extra_info = JSONField(_('extra information'), default={}, blank=True)

    STATUS_PENDING = 'pending'
    STATUS_CLOSED = 'closed'
    STATUS_FAILED = 'failed'
    STATUS_SUCCEEDED = 'succeeded'

    STATUSES = (
        (STATUS_PENDING, _('PaymentStatus|pending')),
        (STATUS_CLOSED, _('PaymentStatus|closed')),
        (STATUS_FAILED, _('PaymentStatus|failed')),
        (STATUS_SUCCEEDED, _('PaymentStatus|succeeded')),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUSES,
                              default=STATUS_PENDING)

    @staticmethod
    def status_changed(old_obj, new_obj):
        if new_obj.status == Payment.STATUS_SUCCEEDED:
            # payment succeeded, mark the order as paid
            new_obj.order.status = Order.STATUS_PAID
            new_obj.order.paid_amount = new_obj.amount
            new_obj.order.save()
        elif new_obj.status in (Payment.STATUS_CLOSED,
                                Payment.STATUS_FAILED):
            # payment closed or failed, refund balance and point
            new_obj.order.user.info.point += new_obj.point_used
            new_obj.order.user.info.balance += new_obj.amount_from_balance
            new_obj.order.user.info.save()

            # clean payment object, in case of duplicated refund
            new_obj.point_used = 0
            new_obj.amount_from_point = 0.0
            new_obj.amount_from_balance = 0.0

    def __str__(self):
        return _('Payment #%(pk)s') % {'pk': self.pk}


@receiver(signals.pre_save, sender=Payment)
def order_pre_save(instance, **kwargs):
    old_instance = None
    if instance.pk:
        old_instance = Payment.objects.get(pk=instance.pk)

    if old_instance and old_instance.status != instance.status:
        instance.status_changed(old_instance, instance)
