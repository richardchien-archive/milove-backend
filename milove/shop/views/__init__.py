import os
import hashlib

from django.conf.urls import url
from django import forms
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..validators import validate_uploaded_file_size
from ..file_storage import storage
from .helpers import validate_or_raise
from . import (
    product,
    user,
    address,
    payment_method,
    order,
    coupon,
    payment,
    sell_request,
    misc_info,
    withdrawal,
)


@ensure_csrf_cookie
@api_view(['GET', 'POST'])
def get_token(request):
    # this should be called every time
    # before the frontend doing a POST request
    # to ensure the frontend has a valid CSRF token
    return Response()


class UploadImageForm(forms.Form):
    file = forms.ImageField(required=True,
                            validators=[validate_uploaded_file_size])


@api_view(['POST'])
def upload(request):
    if not request.user.is_authenticated:
        raise exceptions.NotAuthenticated

    form = UploadImageForm(request.POST, request.FILES)
    validate_or_raise(form)

    file = request.FILES['file']
    filename, ext = os.path.splitext(file.name)
    now = datetime.now()
    filename_hash = hashlib.md5()
    filename_hash.update(file.name.encode('utf-8'))
    filename_hash.update(str(now.timestamp()).encode('utf-8'))
    filename = '{}-{}{}'.format(now.strftime('%Y%m%d%H%M%S'),
                                filename_hash.hexdigest(), ext)

    storage.save(os.path.join('uploads', filename), file)
    return Response({'path': 'uploads/' + filename})


urlpatterns = [
    url(r'^get_token/$', get_token),
    url(r'^upload/$', upload),
]
urlpatterns += product.urlpatterns
urlpatterns += user.urlpatterns
urlpatterns += address.urlpatterns
urlpatterns += payment_method.urlpatterns
urlpatterns += order.urlpatterns
urlpatterns += coupon.urlpatterns
urlpatterns += payment.urlpatterns
urlpatterns += sell_request.urlpatterns
urlpatterns += misc_info.urlpatterns
urlpatterns += withdrawal.urlpatterns
