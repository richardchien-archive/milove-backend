from django.utils.translation import ugettext_lazy as _
from django.db import models
from solo.models import SingletonModel

__all__ = ['MiscInfo']


class MiscInfo(SingletonModel):
    class Meta:
        verbose_name = _('misc information')

    promotion = models.CharField(_('promotion message'), max_length=200,
                                 blank=True)

    def __str__(self):
        return 'Misc Information'
