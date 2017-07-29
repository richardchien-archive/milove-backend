from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

__all__ = ['PaymentMethod']


class PaymentMethod(models.Model):
    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='payment_methods',
                             verbose_name=_('user'))

    name = models.CharField(_('name'), max_length=200)

    PAYPAL = 'paypal'
    CREDIT_CARD = 'credit-card'
    ALIPAY = 'alipay'

    # currently only Stripe credit card can be saved
    METHODS = (
        (CREDIT_CARD, _('credit card')),
    )

    method = models.CharField(_('PaymentMethod|method'),
                              max_length=20, choices=METHODS)
    info = JSONField(_('PaymentMethod|information'), default={}, blank=True)
    secret = JSONField(_('PaymentMethod|secret information'),
                       default={}, blank=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.method)
