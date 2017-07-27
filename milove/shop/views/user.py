from django.contrib import auth
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from ..serializers import UserSerializer
from ..validators import UsernameValidator

router = DefaultRouter()


class SignupForm(forms.Form):
    username = forms.CharField(validators=[UsernameValidator()])
    email = forms.EmailField()
    password = forms.CharField()


class LoginForm(forms.Form):
    username = forms.CharField()  # may be username or email
    password = forms.CharField()


class IsSelf(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and obj.pk == request.user.pk


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelf]

    @list_route(methods=['POST'])
    def signup(self, request):
        form = SignupForm(request.data)
        invalid_fields = []

        if not form.is_valid():
            invalid_fields.extend(list(form.errors.keys()))

        if 'password' not in invalid_fields:
            try:
                validate_password(form.cleaned_data['password'])
            except ValidationError:
                invalid_fields.append('password')

        if 'username' not in invalid_fields:
            if User.objects.filter(
                    username=form.cleaned_data['username']).exists():
                invalid_fields.append('username')
        if 'email' not in invalid_fields:
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                invalid_fields.append('email')

        if invalid_fields:
            raise rest_exceptions.ValidationError(detail={
                'invalid_fields': invalid_fields
            })

        # this may raise DatabaseError,
        # but we should let it produce 500 Internal Server Error,
        # because we have already checked uniqueness of username and email
        user = User.objects.create_user(**form.cleaned_data)
        return Response(UserSerializer(user).data)

    @list_route(['POST'])
    def login(self, request):
        form = LoginForm(request.data)
        if not form.is_valid():
            raise rest_exceptions.ValidationError(detail={
                'invalid_fields': list(form.errors.keys())
            })

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


router.register('users', UserViewSet, base_name='user')

urlpatterns = router.urls
