from django.contrib import auth
from django import forms
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import list_route, detail_route
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.routers import DefaultRouter
from rest_framework.generics import get_object_or_404

from .. import serializers
from ..models import User

router = DefaultRouter()


class LoginForm(forms.Form):
    username = forms.CharField()  # may be username or email
    password = forms.CharField()


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated \
               and obj.pk == request.user.pk


class UserViewSet(mixins.RetrieveModelMixin,  # this brings GET /users/:pk/
                  mixins.UpdateModelMixin,  # this brings PUT and PATCH
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsCurrentUser]

    @list_route(methods=['POST'])
    def signup(self, request):
        serializer = serializers.UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            raise rest_exceptions.ValidationError(detail=serializer.errors)

        user = serializer.save()
        return Response(serializers.UserSerializer(user).data)

    @list_route(['POST'])
    def login(self, request):
        form = LoginForm(request.data)
        if not form.is_valid():
            raise rest_exceptions.ValidationError(detail=form.errors)

        user = auth.authenticate(request,
                                 username=form.cleaned_data['username'],
                                 password=form.cleaned_data['password'])
        if not user:
            raise rest_exceptions.AuthenticationFailed

        auth.login(request, user)
        return Response(serializers.UserSerializer(user).data)

    @list_route(['POST'])
    def logout(self, request):
        auth.logout(request)
        return Response()

    @detail_route(['POST'])
    def change_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        serializer = serializers.UserChangePasswordSerializer(
            instance=user,
            data=request.data
        )
        if not serializer.is_valid():
            raise rest_exceptions.ValidationError(detail=serializer.errors)
        serializer.save()
        return Response()


router.register('users', UserViewSet)

urlpatterns = router.urls
