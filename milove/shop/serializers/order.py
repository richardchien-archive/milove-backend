from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from ..models.order import *
from ..models.product import Product
from ..models.address import Address
from ..models.coupon import Coupon
from ..serializers.product import ProductSerializer
from .helpers import PrimaryKeyRelatedFieldFilterByUser
from .. import mail_shortcuts as mail
from ..thread_pool import delay_run

__all__ = ['ShippingAddressSerializer',
           'OrderSerializer', 'OrderAddSerializer']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ('id', 'order')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        exclude = ('id', 'order')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        exclude = ('user', 'last_status')
        read_only_fields = ('status',
                            'total_price', 'discount_amount',
                            'created_dt', 'shipping_address',
                            'express_company', 'tracking_number')

    def update(self, instance, validated_data):
        if instance.status in (Order.STATUS_UNPAID, Order.STATUS_PAID):
            # in "unpaid" or "paid" status, can update comment
            instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


class OrderAddSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(sold=False),
        write_only=True,
        many=True, allow_empty=False,
    )

    # this is actually an "Address", not a "ShippingAddress"
    shipping_address = PrimaryKeyRelatedFieldFilterByUser(
        queryset=Address.objects.all(),
    )

    coupon = serializers.CharField(
        required=False,
        write_only=True,
    )

    class Meta:
        model = Order
        fields = ('user', 'products', 'shipping_address', 'comment', 'coupon')
        extra_kwargs = {
            'user': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            },
            'comment': {
                'required': False
            }
        }

    def create(self, validated_data):
        products = list(OrderedDict.fromkeys(validated_data['products']))

        # we just checkout the first product passed in,
        # which may be a temporary behavior
        products = products[:1]

        user = validated_data['user']
        comment = validated_data.get('comment', '')
        with transaction.atomic():
            order_items = []
            total_price = 0.0
            for prod in products:
                order_items.append(OrderItem(
                    product=prod,
                    price=prod.price
                ))
                total_price += prod.price
                prod.sold = True
                prod.save()

            discount_amount = 0.0
            if 'coupon' in validated_data:
                # apply coupon if valid
                coupon = Coupon.objects.filter(
                    code=validated_data['coupon'], is_valid=True).first()
                if coupon:
                    discount_amount = coupon.calculate_discount_amount(
                        total_price)

            order = Order.objects.create(
                user=user,
                total_price=total_price,
                discount_amount=discount_amount,
                comment=comment
            )

            for item in order_items:
                item.order = order
                item.save()

            # snapshot the specified "Address", as a "ShippingAddress"
            address = validated_data['shipping_address']
            ShippingAddress.objects.create(
                order=order,
                fullname=address.fullname,
                phone_number=address.phone_number,
                country=address.country,
                street_address=address.street_address,
                city=address.city,
                province=address.province,
                zip_code=address.zip_code
            )

        # notify related user and staffs
        mail.notify_order_created(order)

        def close_unpaid_order(o):
            if o.status == Order.STATUS_UNPAID:
                o.status = Order.STATUS_CLOSED
                o.save()

        if not settings.DEBUG:
            # if the order is still unpaid after some time, close it
            delay_run(settings.ORDER_TIMEOUT, close_unpaid_order, order)

        return order
