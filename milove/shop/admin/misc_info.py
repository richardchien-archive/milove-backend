from django.contrib import admin
from solo.admin import SingletonModelAdmin

from ..models.misc_info import *

admin.site.register(MiscInfo, SingletonModelAdmin)
