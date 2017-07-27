import jsonfield
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from ..validators import UsernameValidator

# hack User model
# https://stackoverflow.com/questions/1160030/how-to-make-email-field-unique-in-model-user-from-contrib-auth-in-django
User._meta.get_field('username').__dict__['validators'] = [UsernameValidator()]
User._meta.get_field('username').__dict__['help_text'] = _(
    'Required. 150 characters or fewer. '
    'Letters, digits and ./+/-/_ only.')
User._meta.get_field('email').__dict__['blank'] = False  # make email required
User._meta.get_field('email').__dict__['_unique'] = True  # make email unique
User._meta.get_field('email').__dict__['error_messages'] = {
    'unique': _("A user with that email already exists."),
}


class UserInfo(models.Model):
    class Meta:
        verbose_name = _('user information')
        verbose_name_plural = _('user information')

    user = models.OneToOneField(User, primary_key=True, related_name='info',
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    balance = models.FloatField(default=0.0,
                                verbose_name=_('UserInfo|balance'))
    point = models.IntegerField(default=0, verbose_name=_('UserInfo|point'))
    contact = jsonfield.JSONField(default={}, blank=True, help_text=' ',
                                  verbose_name=_('UserInfo|contact'))

    def __str__(self):
        return str(self.user)


@receiver(signals.post_save, sender=User)
def create_default_user_info(instance: User, **_):
    if not hasattr(instance, 'info'):
        # there is no UserInfo object bound to the current User, create one
        UserInfo.objects.create(user=instance)
