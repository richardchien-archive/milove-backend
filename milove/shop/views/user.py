from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django import forms
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import list_route, detail_route
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.routers import DefaultRouter
from rest_framework.generics import get_object_or_404

from .. import mail_shortcuts as mail
from ..serializers.user import *
from ..auth import User
from .helpers import validate_or_raise

router = DefaultRouter()


class LoginForm(forms.Form):
    username = forms.CharField()  # may be username or email
    password = forms.CharField()


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated \
               and obj.pk == request.user.pk


class UserViewSet(mixins.RetrieveModelMixin,  # this brings GET /users/:pk/
                  mixins.UpdateModelMixin,  # this brings PUT and PATCH
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsCurrentUser,)

    @list_route(methods=['POST'])
    def signup(self, request):
        # TODO: 可以换成 create 方法，更标准
        serializer = UserSignupSerializer(data=request.data)
        validate_or_raise(serializer)

        user = serializer.save()
        mail.notify_signed_up(user)  # TODO: 可以放在 User 的 post_add 里
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
        return Response(UserSerializer(user).data)

    @list_route(['POST'])
    def logout(self, request):
        auth.logout(request)
        return Response()

    @detail_route(['POST'])
    def change_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        serializer = UserChangePasswordSerializer(
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
        mail.notify_reset_password(
            user=user,
            token=default_token_generator.make_token(user)
        )
        return Response()

    @detail_route(['POST'], permission_classes=())
    def set_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)

        serializer = UserSetPasswordSerializer(user, request.data)
        validate_or_raise(serializer)
        serializer.save()
        return Response()


router.register('users', UserViewSet)

urlpatterns = router.urls
