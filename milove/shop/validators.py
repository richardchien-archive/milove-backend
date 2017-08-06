from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.conf import settings
from django.core.exceptions import ValidationError


class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.+-]+$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    )


def validate_uploaded_file_size(value):
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(_('File %(name)s is too large.'),
                              params={'name': value.name})


def validate_json_object(value):
    if not isinstance(value, dict):
        raise ValidationError(_('This field must be a JSON object.'))


def validate_json_array(value):
    if not isinstance(value, list):
        raise ValidationError(_('This field must be a JSON array.'))
