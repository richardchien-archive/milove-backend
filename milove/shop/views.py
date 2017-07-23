import os
import hashlib

from rest_framework import viewsets, exceptions, parsers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.contrib import auth
from django.middleware import csrf
from django import forms
from django.conf import settings
from django.utils.datetime_safe import datetime
from django.db import transaction

from .models import *
from .serializers import *


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET'])
def get_token(request):
    return Response({'token': csrf.get_token(request)})


@api_view(['POST'])
def login(request):
    if 'username' not in request.data or 'password' not in request.data:
        raise exceptions.ParseError

    user = auth.authenticate(request, username=request.data['username'], password=request.data['password'])
    if not user:
        raise exceptions.AuthenticationFailed

    auth.login(request, user)
    return Response(UserInfoSerializer(user.info).data)


@api_view(['GET'])
def get_user_info(request):
    if not request.user.is_authenticated:
        raise exceptions.NotAuthenticated
    return Response(UserInfoSerializer(request.user.info).data)


@api_view(['POST'])
def logout(request):
    auth.logout(request)
    return Response()


class UploadImageForm(forms.Form):
    file = forms.ImageField(required=True)


@api_view(['POST'])
def upload(request):
    if not request.user.is_authenticated:
        raise exceptions.NotAuthenticated

    form = UploadImageForm(request.POST, request.FILES)
    if not form.is_valid():
        raise exceptions.ParseError

    file = request.FILES['file']
    filename, ext = os.path.splitext(file.name)
    now = datetime.now()
    filename_hash = hashlib.md5()
    filename_hash.update(file.name.encode('utf-8'))
    filename_hash.update(str(now.timestamp()).encode('utf-8'))
    filename = '{}-{}{}'.format(now.strftime('%Y%m%d%H%M%S'), filename_hash.hexdigest(), ext)
    with open(os.path.join(settings.MEDIA_ROOT, 'uploads', filename), 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    return Response({'path': 'uploads/' + filename})
