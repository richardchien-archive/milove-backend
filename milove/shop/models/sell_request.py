from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from jsonfield import JSONField

from .product import Product
from .address import AbstractAddress
from .. import mail_shortcuts as mail

__all__ = ['SellRequest', 'get_direct_dst_statuses', 'get_direct_src_statuses',
           'is_status_transition_allowed']


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

    buy_back_valuation = models.FloatField(_('SellRequest|buy back valuation'),
                                           null=True, blank=True)
    sell_valuation = models.FloatField(_('SellRequest|sell valuation'),
                                       null=True, blank=True)
    valuated_dt = models.DateTimeField(_('SellRequest|valuated datetime'),
                                       null=True, blank=True)

    SELL_TYPE_UNDECIDED = 'undecided'
    SELL_TYPE_BUY_BACK = 'buy-back'
    SELL_TYPE_SELL = 'sell'

    SELL_TYPES = (
        (SELL_TYPE_UNDECIDED, _('SellRequest|undecided')),
        (SELL_TYPE_BUY_BACK, _('SellRequest|buy back')),
        (SELL_TYPE_SELL, _('SellRequest|sell')),
    )

    sell_type = models.CharField(_('SellRequest|sell type'), max_length=20,
                                 choices=SELL_TYPES,
                                 default=SELL_TYPE_UNDECIDED)

    def __str__(self):
        return ('#%s ' % self.pk) + self.brand \
               + (' ' + self.name if self.name else '')


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


def get_direct_src_statuses(status):
    """Get statuses that can directly transition to the given status."""
    if status not in _STATUSES:
        return ()
    return (status,) + tuple(map(
        lambda side: side[0],
        filter(lambda side: side[1] == status, _STATUS_SIDES)
    ))


def get_direct_dst_statuses(status):
    """Get statuses that the given status can directly transition to."""
    if status not in _STATUSES:
        return ()
    return (status,) + tuple(map(
        lambda side: side[1],
        filter(lambda side: side[0] == status, _STATUS_SIDES)
    ))


def is_status_transition_allowed(src_status, dst_status):
    """Check if the transition from "src_status" to "dst_status" is allowed."""
    if src_status not in _STATUSES or dst_status not in _STATUSES:
        return False
    return src_status == dst_status or any(
        map(lambda side: side[0] == src_status and side[1] == dst_status,
            _STATUS_SIDES)
    )
