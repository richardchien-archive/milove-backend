import os
import hashlib

from django.conf.urls import url
from django import forms
from django.conf import settings
from django.utils.datetime_safe import datetime
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, exceptions, parsers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response

from . import (
    product,
    user,
    address,
    payment_method,
    order,
    coupon,
)


@ensure_csrf_cookie
@api_view(['GET', 'POST'])
def get_token(request):
    # this should be called every time
    # before the frontend doing a POST request
    # to ensure the frontend has a valid CSRF token
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
    filename = '{}-{}{}'.format(now.strftime('%Y%m%d%H%M%S'),
                                filename_hash.hexdigest(), ext)
    with open(os.path.join(settings.MEDIA_ROOT, 'uploads', filename),
              'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    return Response({'path': 'uploads/' + filename})


urlpatterns = [
    url(r'^get_token/$', get_token),
]
urlpatterns += product.urlpatterns
urlpatterns += user.urlpatterns
urlpatterns += address.urlpatterns
urlpatterns += payment_method.urlpatterns
urlpatterns += order.urlpatterns
urlpatterns += coupon.urlpatterns
