from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from ..models.user import *


class UserInfoAdmin(admin.ModelAdmin):
    def get_id(self, instance: UserInfo):
        return instance.user_id

    get_id.short_description = _('id')
    get_id.admin_order_field = 'user__id'

    def get_username(self, instance: UserInfo):
        return instance.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_email(self, instance: UserInfo):
        return instance.user.email

    get_email.short_description = _('email')
    get_email.admin_order_field = 'user__email'

    def get_contact_string(self, instance: UserInfo):
        if not instance.contact:
            return '-'
        return '; '.join(['%s: %s' % (k, v)
                          for k, v in instance.contact.items()])

    get_contact_string.short_description = _('UserInfo|contact')

    list_display = ('get_id', 'get_username', 'get_email',
                    'nickname', 'balance', 'point', 'get_contact_string')
    list_display_links = ('get_id', 'get_username', 'get_email')
    ordering = ('user__id',)
    search_fields = ('user__username', 'user__email', 'nickname')


admin.site.register(UserInfo, UserInfoAdmin)

# hack UserAdmin
UserAdmin.list_display = ('id', 'username', 'email',
                          'date_joined', 'last_login',
                          'is_active', 'is_staff')
UserAdmin.list_display_links = ('id', 'username', 'email')
UserAdmin.ordering = ('id',)
UserAdmin.list_filter = UserAdmin.list_filter + ('date_joined', 'last_login')
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'password1', 'password2'),
    }),
)
UserAdmin.fieldsets = (
    (None, {'fields': ('username', 'email', 'password')}),
    (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
    (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
)
