from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class Backend(ModelBackend):
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
