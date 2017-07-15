from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class UserInfo(models.Model):
    class Meta:
        verbose_name = _('user information')
        verbose_name_plural = _('user information')

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, verbose_name=_('user'))

    def get_id(self):
        return self.user.id

    get_id.short_description = _('id')
    get_id.admin_order_field = 'user__id'

    def get_username(self):
        return self.user.username

    get_username.short_description = _('username')
    get_username.admin_order_field = 'user__username'

    def get_email(self):
        return self.user.email

    get_email.short_description = _('email')
    get_email.admin_order_field = 'user__email'

    nickname = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('nickname'))
    balance = models.FloatField(default=0.0, verbose_name=_('UserInfo|balance'))
    point = models.IntegerField(default=0, verbose_name=_('UserInfo|point'))

    def __str__(self):
        return self.get_username()
