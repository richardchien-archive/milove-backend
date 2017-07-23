from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ..models.user import *


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('get_id', 'get_username', 'get_email', 'nickname', 'balance', 'point')
    list_display_links = ('get_id', 'get_username')
    ordering = ('user__id',)


class UserInfoInline(admin.StackedInline):
    model = UserInfo


UserAdmin.inlines = (UserInfoInline,)
UserAdmin.list_display = ('id',) + UserAdmin.list_display
UserAdmin.list_display_links = ('id', 'username')
UserAdmin.ordering = ('id',)

admin.site.register(UserInfo, UserInfoAdmin)
