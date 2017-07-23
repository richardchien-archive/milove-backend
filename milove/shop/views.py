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


@api_view(['POST'])
@parser_classes((parsers.JSONParser,))  # we only allow JSON data here
def checkout(request):
    if not request.user.is_authenticated:
        raise exceptions.NotAuthenticated

    if not all((isinstance(request.data.get('products'), list),
                isinstance(request.data.get('use_balance'), bool),
                isinstance(request.data.get('payment_method'), str))):
        raise exceptions.ParseError

    try:
        prods_to_checkout = {int(x) for x in request.data['products']}
        if not prods_to_checkout:
            # there are no products specified
            raise ValueError
    except ValueError:
        raise exceptions.ParseError

    payment_method = request.data['payment_method'].upper()
    for method in Order.PAYMENT_METHODS:
        if method[0] == payment_method:
            break
    else:
        raise exceptions.ParseError

    prods_not_exist = set()
    prods_sold = set()
    prods = Product.objects.filter(pk__in=prods_to_checkout)
    if prods.count() < len(prods_to_checkout):
        # some of the submitted products don't exist
        prod_pks = {p.pk for p in prods}
        prods_not_exist = prods_to_checkout - prod_pks

    for prod in prods:
        if prod.sold:
            prods_sold.add(prod.pk)

    if prods_not_exist or prods_sold:
        return Response({'not_exist': prods_not_exist, 'sold': prods_sold})

    order = Order(user=request.user, payment_method=payment_method,
                  use_balance=request.data['use_balance'], from_balance=0.0,
                  total_price=0.0, status=Order.STATUS_UNPAID)

    with transaction.atomic():
        with transaction.atomic():
            # mark all products involved as 'sold'
            for prod in prods:
                prod.sold = True
                prod.save()

        order.save()

        for prod in prods:
            order.total_price += prod.price
            item = OrderItem(product=prod, order=order, price=prod.price)
            item.save()
            order.items.add(item)

        use_balance = request.data['use_balance']
        if use_balance:
            balance = 0.0
            if request.user.info:
                balance = request.user.info.balance
            order.from_balance = min((balance, order.total_price))
            if balance >= order.total_price:
                # all from balance, pay immediately
                request.user.info.balance -= order.from_balance
                request.user.info.save()
                order.status = Order.STATUS_PAID
        if order.total_price == 0.0:
            order.status = Order.STATUS_PAID
        order.save()

    return Response(order.pk)
