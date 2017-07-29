from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ['Address']


class AbstractAddress(models.Model):
    class Meta:
        abstract = True

    fullname = models.CharField(_('Address|fullname'), max_length=100)
    phone_number = models.CharField(_('phone number'), max_length=30)

    COUNTRY_US = 'US'
    COUNTRY_CA = 'CA'
    COUNTRIES = (
        (COUNTRY_US, _('United State')),
        (COUNTRY_CA, _('Canada')),
    )

    country = models.CharField(_('Address|country'),
                               max_length=3, choices=COUNTRIES)

    street_address = models.CharField(_('Address|street address'),
                                      max_length=200)
    city = models.CharField(_('Address|city'), max_length=100)
    province = models.CharField(_('Address|province'), max_length=100)
    zip_code = models.CharField(_('Address|ZIP code'), max_length=20)

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.fullname,
            self.city,
            self.province,
            self.country
        )


class Address(AbstractAddress):
    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name=_('user'))
