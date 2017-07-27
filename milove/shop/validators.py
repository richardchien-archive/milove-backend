from django.utils.translation import ugettext_lazy as _
from django.core import validators


class UsernameValidator(validators.RegexValidator):
    regex = r'^[_a-zA-Z0-9]+$'
    message = _(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and underline character (_).'
    )
