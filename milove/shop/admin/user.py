from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from ..models.user import UserInfo
from ..auth import User


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email',
                    'date_joined', 'last_login',
                    'is_active', 'is_staff')
    list_display_links = ('id', 'username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups',
                   'date_joined', 'last_login')
    ordering = ('id',)
    search_fields = ('username', 'email')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, UserAdmin)


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
        if not isinstance(instance.contact, dict):
            return str(instance.contact)
        return '; '.join(['%s: %s' % (k, v)
                          for k, v in instance.contact.items()])

    get_contact_string.short_description = _('UserInfo|contact')

    list_display = ('get_id', 'get_username', 'get_email',
                    'balance', 'point', 'get_contact_string')
    list_display_links = ('get_id', 'get_username', 'get_email')
    ordering = ('user__id',)
    search_fields = ('user__username', 'user__email')


admin.site.register(UserInfo, UserInfoAdmin)
