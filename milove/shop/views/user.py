from django.contrib import auth
from django.conf.urls import url
from django import forms
from rest_framework import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import UserSerializer
from ..auth import api_login_required
from ..validators import UsernameValidator


class LoginForm(forms.Form):
    username = forms.CharField()  # may be username or email
    password = forms.CharField()


@api_view(['POST'])
def login(request):
    form = LoginForm(request.data)
    if not form.is_valid():
        raise exceptions.ParseError

    user = auth.authenticate(request,
                             username=form.cleaned_data['username'],
                             password=form.cleaned_data['password'])
    if not user:
        raise exceptions.AuthenticationFailed

    auth.login(request, user)
    return Response(UserSerializer(user).data)


@api_view(['GET'])
@api_login_required
def get_user_info(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def logout(request):
    auth.logout(request)
    return Response()


class SignupForm(forms.Form):
    username = forms.CharField(validators=[UsernameValidator()])
    email = forms.EmailField()
    password = forms.CharField()


# @api_view(['POST'])
# def signup(request):
#     form = SignupForm(request.data)
#     if not form.is_valid():
#         raise exceptions.ParseError
#
#
#     return Response()


urlpatterns = [
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^get_user_info/$', get_user_info),
]
