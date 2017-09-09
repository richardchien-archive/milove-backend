from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver

from .. import mail_shortcuts as mail

__all__ = ['Withdrawal']


class Withdrawal(models.Model):
    class Meta:
        verbose_name = _('withdrawal')
        verbose_name_plural = _('withdrawals')

    created_dt = models.DateTimeField(_('created datetime'), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             related_name='withdrawals',
                             on_delete=models.SET_NULL, verbose_name=_('user'))

    amount = models.FloatField(_('Withdrawal|amount'))
    processed_amount = models.FloatField(_('Withdrawal|processed amount'),
                                         default=0.0)

    METHOD_PAYPAL = 'paypal'
    METHOD_ALIPAY = 'alipay'
    METHOD_OTHER = 'other'

    METHODS = (
        (METHOD_PAYPAL, _('PayPal')),
        (METHOD_ALIPAY, _('Alipay')),
        (METHOD_OTHER, _('Other')),
    )

    method = models.CharField(_('Withdrawal|method'),
                              max_length=20, choices=METHODS)
    vendor_account = models.CharField(_('Withdrawal|vendor account'),
                                      max_length=200)

    STATUS_PENDING = 'pending'
    STATUS_CLOSED = 'closed'
    STATUS_DONE = 'done'

    STATUSES = (
        (STATUS_PENDING, _('WithdrawalStatus|pending')),
        (STATUS_CLOSED, _('WithdrawalStatus|closed')),
        (STATUS_DONE, _('WithdrawalStatus|done')),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUSES,
                              default=STATUS_PENDING)

    def clean(self):
        if self.processed_amount > self.amount:
            raise ValidationError(_('Processed amount cannot '
                                    'be larger than amount.'))

    @staticmethod
    def status_changed(old_obj, new_obj):
        if new_obj.status == Withdrawal.STATUS_CLOSED:
            # rollback the balance
            new_obj.user.info.increase_balance(
                max(0, new_obj.amount - new_obj.processed_amount))

    def __str__(self):
        return _('Withdrawal #%(pk)s') % {'pk': self.pk}


@receiver(signals.pre_save, sender=Withdrawal)
def withdrawal_pre_save(instance, **kwargs):
    old_instance = None
    if instance.pk:
        old_instance = Withdrawal.objects.get(pk=instance.pk)

    if old_instance and old_instance.status != instance.status:
        instance.status_changed(old_instance, instance)


@receiver(signals.post_save, sender=Withdrawal)
def withdrawal_post_save(instance, created, **kwargs):
    if created:
        # notify related user and staffs
        mail.notify_withdrawal_created(instance)
