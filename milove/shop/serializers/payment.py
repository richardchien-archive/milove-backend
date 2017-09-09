from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from .helpers import PrimaryKeyRelatedFieldFilterByUser
from ..models.payment import *
from ..models.order import Order
from ..models.address import Address
from ..models.payment_method import PaymentMethod
from ..exceptions import PaymentFailed
from ..payment_funcs import charge_balance_and_point, get_payment_func
from ..thread_pool import delay_run

__all__ = ['PaymentSerializer', 'PaymentAddSerializer']


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        exclude = ('id', 'payment')


class PaymentSerializer(serializers.ModelSerializer):
    billing_address = BillingAddressSerializer(read_only=True)

    class Meta:
        model = Payment
        exclude = ('extra_info',)


class PaymentAddSerializer(serializers.ModelSerializer):
    order = PrimaryKeyRelatedFieldFilterByUser(
        queryset=Order.objects.filter(status=Order.STATUS_UNPAID)
    )

    # this is actually an "Address", not a "BillingAddress"
    billing_address = PrimaryKeyRelatedFieldFilterByUser(
        queryset=Address.objects.all(),
        write_only=True
    )

    # if the balance and point is enough to pay the bill, this can be null,
    # but if not, and meanwhile this is null, payment will fail immediately
    method = serializers.ChoiceField(choices=Payment.METHODS, allow_null=True)

    # for savable payment method (e.g. Stripe credit card),
    # the user must specify a saved method (card) to use in the frontend.
    # if the method is not savable (e.g. PayPal), this must be null
    method_id = PrimaryKeyRelatedFieldFilterByUser(
        queryset=PaymentMethod.objects.all(),
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Payment
        fields = ('order', 'billing_address', 'use_balance',
                  'use_point', 'method', 'method_id')
        extra_kwargs = {
            # no matter use or not, the following 2 fields must be passed in
            'use_balance': {
                'required': True
            },
            'use_point': {
                'required': True
            }
        }

    def create(self, validated_data):
        required_keys = {'order', 'billing_address', 'use_balance',
                         'use_point', 'method', 'method_id'}
        assert required_keys == required_keys.intersection(
            validated_data.keys())

        order = validated_data['order']
        user = order.user
        amount_to_pay = order.total_price - order.discount_amount

        payment = Payment(
            order=order,
            amount=amount_to_pay,
            use_point=validated_data['use_point'],
            use_balance=validated_data['use_balance'],
            method=validated_data['method']
        )

        if payment.use_point:
            payment.amount_from_point = min(
                amount_to_pay, settings.POINT_TO_AMOUNT(user.info.point)
            )
            amount_to_pay -= payment.amount_from_point

        if payment.use_balance and amount_to_pay > 0:
            payment.amount_from_balance = min(amount_to_pay,
                                              user.info.balance)
            amount_to_pay -= payment.amount_from_balance

        with transaction.atomic():
            # do create the payment object in db
            payment.save()

            # snapshot the specified "Address", as a "ShippingAddress"
            address = validated_data['billing_address']
            BillingAddress.objects.create(
                payment=payment,
                fullname=address.fullname,
                phone_number=address.phone_number,
                country=address.country,
                street_address=address.street_address,
                city=address.city,
                province=address.province,
                zip_code=address.zip_code
            )

        try:
            if amount_to_pay > 0:
                # the remained amount will be charged from 3-party

                # we don't call charge_balance_and_point() here,
                # the payment function will do this

                method_obj = validated_data['method_id']
                if method_obj and method_obj.method != payment.method:
                    raise PaymentFailed

                func = get_payment_func(payment.method)
                if not func:
                    raise PaymentFailed
                func(
                    payment=payment,
                    method_obj=method_obj,
                    amount=amount_to_pay
                )
            else:
                # pay with balance and point
                charge_balance_and_point(payment)
                # no exception raised, means succeeded
                payment.status = Payment.STATUS_SUCCEEDED
        except PaymentFailed:
            payment.status = Payment.STATUS_FAILED
            raise
        finally:
            # no matter what happened, save the payment
            payment.save()

        def close_pending_payment(p):
            p.refresh_from_db(fields=('status',))
            if p.status == Payment.STATUS_PENDING:
                p.status = Payment.STATUS_CLOSED
                p.save()

        if not settings.DEBUG and payment.status == Payment.STATUS_PENDING:
            # if the payment is still pending after some time, close it
            delay_run(settings.PAYMENT_TIMEOUT, close_pending_payment, payment)

        return payment
