from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django import forms
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import list_route, detail_route
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.routers import SimpleRouter
from rest_framework.generics import get_object_or_404

from .. import mail_shortcuts as mail
from ..serializers.user import *
from ..auth import User
from .helpers import validate_or_raise

router = SimpleRouter()


class LoginForm(forms.Form):
    username = forms.CharField()  # may be username or email
    password = forms.CharField()


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated \
               and obj.pk == request.user.pk


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsCurrentUser,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSignupSerializer
        return self.serializer_class

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        validate_or_raise(serializer)

        user = serializer.save()
        mail.notify_user_signed_up(user)
        return Response(UserSerializer(user).data,
                        status=status.HTTP_201_CREATED)

    @list_route(['POST'])
    def login(self, request):
        form = LoginForm(request.data)
        validate_or_raise(form)

        user = auth.authenticate(request,
                                 username=form.cleaned_data['username'],
                                 password=form.cleaned_data['password'])
        if not user:
            raise rest_exceptions.AuthenticationFailed

        auth.login(request, user)
        return Response(self.get_serializer(user).data)

    @list_route(['GET'], permission_classes=(IsAuthenticated,))
    def current(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @list_route(['POST'])
    def logout(self, request):
        auth.logout(request)
        return Response()

    @detail_route(['POST'], serializer_class=UserChangePasswordSerializer)
    def change_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(
            instance=user,
            data=request.data
        )
        validate_or_raise(serializer)
        serializer.save()
        auth.update_session_auth_hash(request, user)  # prevent log out
        return Response()

    @list_route(['POST'])
    def forgot_password(self, request):
        form = ForgotPasswordForm(request.data)
        validate_or_raise(form)

        user = get_object_or_404(User, email=form.cleaned_data['email'])
        mail.notify_user_reset_password(
            user=user,
            token=default_token_generator.make_token(user)
        )
        return Response()

    @detail_route(['POST'], permission_classes=(),
                  serializer_class=UserSetPasswordSerializer)
    def set_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)

        serializer = self.get_serializer(user, request.data)
        validate_or_raise(serializer)
        serializer.save()
        return Response()


router.register('users', UserViewSet)

urlpatterns = router.urls
