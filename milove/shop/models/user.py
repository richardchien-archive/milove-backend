import jsonfield
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password

from ..validators import UsernameValidator


class User(AbstractUser):
    first_name = None
    last_name = None

    username_validator = UsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. '
                    'Letters, digits and ./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email address already exists."),
        }
    )
    password = models.CharField(_('password'), validators=[validate_password],
                                max_length=128)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.username

    def get_short_name(self):
        "Returns the short name for the user."
        return self.username


class UserInfo(models.Model):
    class Meta:
        verbose_name = _('user information')
        verbose_name_plural = _('user information')

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                primary_key=True,
                                related_name='info',
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    balance = models.FloatField(default=0.0,
                                verbose_name=_('UserInfo|balance'))
    point = models.IntegerField(default=0, verbose_name=_('UserInfo|point'))
    contact = jsonfield.JSONField(default={}, blank=True, help_text=' ',
                                  verbose_name=_('UserInfo|contact'))

    def __str__(self):
        return str(self.user)


@receiver(signals.post_save, sender=settings.AUTH_USER_MODEL)
def create_default_user_info(instance, **_):
    if not hasattr(instance, 'info'):
        # there is no UserInfo object bound to the current User, create one
        UserInfo.objects.create(user=instance)
