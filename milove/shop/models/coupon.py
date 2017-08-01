from django.utils.translation import ugettext_lazy as _
from django.db import models

__all__ = ['Coupon']


class Coupon(models.Model):
    class Meta:
        verbose_name = _('coupon')
        verbose_name_plural = _('coupons')

    code = models.CharField(_('Coupon|code'), max_length=100)

    TYPE_RATE = 'rate'
    TYPE_AMOUNT = 'amount'
    TYPES = (
        (TYPE_RATE, _('Coupon|rate')),
        (TYPE_AMOUNT, _('Coupon|amount')),
    )

    type = models.CharField(_('type'), max_length=10,
                            choices=TYPES, default=TYPE_RATE)
    price_required = models.FloatField(_('Coupon|price required'), default=0.0)
    discount = models.FloatField(_('Coupon|discount'))
    is_valid = models.BooleanField(_('Coupon|is valid'), default=True)

    def __str__(self):
        return '{} {}{} Off'.format(
            self.code,
            self.discount if self.type == Coupon.TYPE_RATE else '$',
            '%' if self.type == Coupon.TYPE_RATE else self.discount,
        )

    def calculate_discount_amount(self, total_price):
        if total_price > self.price_required:
            if self.type == Coupon.TYPE_RATE:
                return round(self.discount / 100 * total_price, 2)
            else:
                return self.discount
        return 0.0
