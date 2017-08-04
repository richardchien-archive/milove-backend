from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from jsonfield import JSONField

from .product import Product
from .address import AbstractAddress
from .. import mail_shortcuts as mail

__all__ = ['SellRequest']


class SellRequest(models.Model):
    class Meta:
        verbose_name = _('sell request')
        verbose_name_plural = _('sell requests')

    created_dt = models.DateTimeField(_('created datetime'), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             related_name='sell_requests',
                             on_delete=models.SET_NULL, verbose_name=_('user'))

    brand = models.CharField(_('Product|brand'), max_length=100)
    category = models.CharField(_('Product|category'), max_length=30)
    name = models.CharField(_('Product|name'), max_length=200, blank=True)
    size = models.CharField(_('Product|size'), max_length=20, blank=True)
    condition = models.CharField(_('Product|condition'), max_length=50)
    year = models.CharField(_('SellRequest|year'), max_length=10)
    original_price = models.FloatField(_('Product|original price'))
    attachments = models.CharField(_('Product|attachments'), max_length=200,
                                   blank=True)
    description = models.TextField(_('Product|description'), blank=True)

    # STATUS_

    buy_back_price = models.FloatField(_('SellRequest|buy back price'),
                                       null=True, blank=True)
    sell_price = models.FloatField(_('SellRequest|sell price'),
                                   null=True, blank=True)

    image_paths = JSONField(_('image paths'), default=[], blank=True)

    def __str__(self):
        return ('#%s ' % self.pk) + self.brand \
               + (' ' + self.name if self.name else '')
