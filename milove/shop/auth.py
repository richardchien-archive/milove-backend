from functools import wraps

from rest_framework import exceptions
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


def api_login_required(func):
    """
    Require login when access API view.

    This only work with Django REST Framework,
    and must be put below the @api_view decorator:

    >>> from rest_framework.decorators import api_view
    >>> @api_view(['GET'])
    >>> @api_login_required
    >>> def get_user_info(request):
    >>>     assert request.user.is_authenticated
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated
        return func(request, *args, **kwargs)

    return wrapper


class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        model = get_user_model()
        if username is None:
            username = kwargs.get(model.USERNAME_FIELD)
        try:
            username_field = 'username'
            if '@' in username:
                username_field = 'email'

            # noinspection PyProtectedMember
            user = model._default_manager.get(**{username_field: username})
        except model.DoesNotExist:
            model().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(
                    user):
                return user
