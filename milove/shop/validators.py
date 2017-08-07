from collections import Iterable

from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage


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


def validate_files_exist(value):
    if not isinstance(value, Iterable):
        return
    storage = DefaultStorage()
    for file in value:
        if not storage.exists(file):
            raise ValidationError(_('File %(name)s does not exist.'),
                                  params={'name': file})
