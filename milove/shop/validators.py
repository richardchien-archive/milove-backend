from django.utils.translation import ugettext_lazy as _
from django.core import validators


class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.+-]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    )
