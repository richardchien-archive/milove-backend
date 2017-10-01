import functools
import os
import hashlib

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from jsonfield import JSONField

from .address import AbstractAddress
from .helpers import *
from ..file_storage import storage
from .. import mail_shortcuts as mail

__all__ = ['SellRequestSenderAddress', 'SellRequest',
           'get_direct_dst_statuses', 'get_direct_src_statuses',
           'is_status_transition_allowed']


class SellRequestSenderAddress(AbstractAddress):
    class Meta:
        verbose_name = _('sell request sender address')
        verbose_name_plural = _('sell request sender addresses')

    sell_request = models.OneToOneField('SellRequest',
                                        on_delete=models.CASCADE,
                                        related_name='sender_address',
                                        verbose_name=_('sell request'))


def _shipping_label_upload_path(instance, filename):
    filename, ext = os.path.splitext(filename)
    now = timezone.now()
    filename_hash = hashlib.md5()
    filename_hash.update(filename.encode('utf-8'))
    filename_hash.update(str(now.timestamp()).encode('utf-8'))
    return 'sell_requests/%s/shipping-label-%s%s' % (
        instance.pk, filename_hash.hexdigest(), ext
    )


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
    condition = models.CharField(_('Product|condition'), max_length=100)
    purchase_year = models.CharField(_('SellRequest|purchase year'),
                                     max_length=10)
    original_price = models.FloatField(_('Product|original price'))
    attachments = models.CharField(_('Product|attachments'), max_length=200,
                                   blank=True)
    description = models.TextField(_('Product|description'), blank=True)
    image_paths = JSONField(_('image paths'), default=[], blank=True)

    def brief_info(self):
        info = []
        for k in ('size', 'condition'):
            v = getattr(self, k, None)
            if v:
                info.append(_('Product|' + k) + ':' + v)
        return ';'.join(info)

    STATUS_CREATED = 'created'
    STATUS_CANCELLED = 'cancelled'
    STATUS_DENIED = 'denied'
    STATUS_VALUATED = 'valuated'
    STATUS_CLOSED = 'closed'
    STATUS_DECIDED = 'decided'
    STATUS_SHIPPING = 'shipping'
    STATUS_AUTHENTICATING = 'authenticating'
    STATUS_SELLING = 'selling'
    STATUS_DONE = 'done'

    STATUSES = (
        (STATUS_CREATED, _('SellRequest|created')),
        (STATUS_CANCELLED, _('SellRequest|cancelled')),
        (STATUS_DENIED, _('SellRequest|denied')),
        (STATUS_VALUATED, _('SellRequest|valuated')),
        (STATUS_CLOSED, _('SellRequest|closed')),
        (STATUS_DECIDED, _('SellRequest|decided')),
        (STATUS_SHIPPING, _('SellRequest|shipping')),
        (STATUS_AUTHENTICATING, _('SellRequest|authenticating')),
        (STATUS_SELLING, _('SellRequest|selling')),
        (STATUS_DONE, _('SellRequest|done')),
    )

    status = models.CharField(_('status'), max_length=20, choices=STATUSES,
                              default=STATUS_CREATED)

    denied_reason = models.TextField(_('SellRequest|denied reason'),
                                     null=True, blank=True)

    buy_back_valuation = models.FloatField(_('SellRequest|buy back valuation'),
                                           null=True, blank=True)
    sell_valuation = models.FloatField(_('SellRequest|sell valuation'),
                                       null=True, blank=True)
    valuated_dt = models.DateTimeField(_('SellRequest|valuated datetime'),
                                       null=True, blank=True)

    SELL_TYPE_BUY_BACK = 'buy-back'
    SELL_TYPE_SELL = 'sell'

    SELL_TYPES = (
        (SELL_TYPE_BUY_BACK, _('SellRequest|buy back')),
        (SELL_TYPE_SELL, _('SellRequest|sell')),
    )

    sell_type = models.CharField(_('SellRequest|sell type'), max_length=20,
                                 choices=SELL_TYPES, null=True, blank=True)

    shipping_label = models.FileField(_('shipping label'),
                                      upload_to=_shipping_label_upload_path,
                                      null=True, blank=True)
    express_company = models.CharField(_('express company'),
                                       null=True, blank=True, max_length=60)
    tracking_number = models.CharField(_('tracking number'),
                                       null=True, blank=True, max_length=30)

    done_dt = models.DateTimeField(_('SellRequest|done datetime'),
                                   null=True, blank=True)

    def __str__(self):
        return ('#%s ' % self.pk) + self.brand \
               + (' ' + self.name if self.name else '')

    @staticmethod
    def status_changed(old_obj, new_obj):
        if new_obj.status == SellRequest.STATUS_VALUATED:
            # log the datetime
            new_obj.valuated_dt = timezone.now()
        elif new_obj.status == SellRequest.STATUS_DONE:
            # the sell request is done
            new_obj.done_dt = timezone.now()
            if new_obj.sell_type == SellRequest.SELL_TYPE_BUY_BACK:
                new_obj.user.info.increase_balance(new_obj.buy_back_valuation)
            elif new_obj.sell_type == SellRequest.SELL_TYPE_SELL:
                new_obj.user.info.increase_balance(new_obj.sell_valuation)


@receiver(signals.pre_save, sender=SellRequest)
def sell_request_pre_save(instance, **kwargs):
    old_instance = None
    if instance.pk:
        old_instance = SellRequest.objects.get(pk=instance.pk)

    if old_instance and old_instance.status != instance.status:
        instance.status_changed(old_instance, instance)

        # notify related user and staffs
        mail.notify_sell_request_status_changed(instance)


@receiver(signals.post_save, sender=SellRequest)
def sell_request_post_save(instance, created, **kwargs):
    if created:
        # notify related user and staffs
        mail.notify_sell_request_created(instance)

        # move uploaded files
        for index, name in enumerate(instance.image_paths):
            if name.startswith('uploads/') and storage.exists(name):
                pure_name = name.split('/')[-1]
                new_dir = 'sell_requests/%s/' % instance.pk
                os.makedirs(storage.path(new_dir), exist_ok=True)
                new_name = new_dir + pure_name
                instance.image_paths[index] = new_name
                os.rename(storage.path(name), storage.path(new_name))
        instance.save()


# all sides of the status transition graph
_STATUS_SIDES = (
    (SellRequest.STATUS_CREATED, SellRequest.STATUS_CANCELLED),
    (SellRequest.STATUS_CREATED, SellRequest.STATUS_DENIED),
    (SellRequest.STATUS_CREATED, SellRequest.STATUS_VALUATED),
    (SellRequest.STATUS_VALUATED, SellRequest.STATUS_CLOSED),
    (SellRequest.STATUS_VALUATED, SellRequest.STATUS_DECIDED),
    (SellRequest.STATUS_DECIDED, SellRequest.STATUS_SHIPPING),
    (SellRequest.STATUS_SHIPPING, SellRequest.STATUS_AUTHENTICATING),
    (SellRequest.STATUS_AUTHENTICATING, SellRequest.STATUS_SELLING),
    (SellRequest.STATUS_AUTHENTICATING, SellRequest.STATUS_DONE),
    (SellRequest.STATUS_SELLING, SellRequest.STATUS_DONE),
)

_STATUSES = dict(SellRequest.STATUSES).keys()

get_direct_src_statuses = functools.partial(base_get_direct_src_statuses,
                                            _STATUSES, _STATUS_SIDES)
get_direct_dst_statuses = functools.partial(base_get_direct_dst_statuses,
                                            _STATUSES, _STATUS_SIDES)
is_status_transition_allowed = functools.partial(
    base_is_status_transition_allowed, _STATUSES, _STATUS_SIDES)
