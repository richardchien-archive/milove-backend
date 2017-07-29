from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import product, user, order, address

admin.site.site_header = admin.site.site_title = _('Milove Admin')
