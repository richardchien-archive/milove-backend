from functools import wraps

from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions, status

from ..models.payment import *
from ..models.order import Order
from ..models.address import Address
from ..models.payment_method import PaymentMethod
from .helpers import PrimaryKeyRelatedFieldFilterByUser
from ..thread_pool import delay_run

__all__ = ['PaymentSerializer', 'PaymentAddSerializer']


class PaymentFailed(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('The payment is failed.')


_payment_funcs = {}


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

    method = serializers.ChoiceField(choices=Payment.METHODS, allow_null=True)
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
            payment.point_used = settings.POINT_TO_AMOUNT_REVERSE(
                payment.amount_from_point
            )
            amount_to_pay -= payment.amount_from_point

        if payment.use_balance and amount_to_pay > 0:
            payment.amount_from_balance = min(amount_to_pay,
                                              user.info.balance)
            amount_to_pay -= payment.amount_from_balance

        with transaction.atomic():
            payment.save()  # do create the payment object in db

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

        user.info.point -= payment.point_used
        user.info.balance -= payment.amount_from_balance
        user.info.save()

        try:
            if amount_to_pay > 0:
                method_obj = validated_data['method_id']
                if method_obj and method_obj.method != payment.method:
                    raise PaymentFailed
                try:
                    _payment_funcs[payment.method](
                        payment=payment,
                        method_obj=method_obj,
                        amount=amount_to_pay
                    )
                    payment.save()
                except (KeyError, PaymentFailed):
                    raise PaymentFailed
            else:
                # already paid all
                payment.status = Payment.STATUS_SUCCEEDED
                payment.save()
        except PaymentFailed:
            # NOTE!
            # balance and point have been subtracted from the user's account,
            # and status_change method will handle the refund job
            payment.status = Payment.STATUS_FAILED
            payment.save()
            raise

        def close_pending_payment(p):
            if p.status == Payment.STATUS_PENDING:
                p.status = Payment.STATUS_CLOSED
                p.save()

        if payment.status == payment.STATUS_PENDING:
            # if the payment is still pending after 5 minutes,
            # close it, and balance and point will be refunded
            delay_run(5 * 60, close_pending_payment, payment)

        return payment


def pay_with(method_name):
    """
    Decorate a function as the payment function of a given payment method.

    The function should receive these keyword arguments:
    - payment: A Payment object
    - method_obj: A PaymentMethod object, or None
    - amount: Amount that should be charged, in USD

    The function should process the payment and change "payment" object
    if needed (especially the "status" and "vendor_payment_id" attributes),
    without need to call "save()" on it.

    If anything wrong happened while creating payment, raise PaymentFailed.

    :param method_name: payment method name
    """

    def decorator(func):
        _payment_funcs[method_name] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@pay_with(PaymentMethod.PAYPAL)
def _pay_with_paypal(payment, amount, **kwargs):
    import paypalrestsdk as paypal
    paypal_payment = paypal.Payment({
        'intent': 'sale',
        'redirect_urls': {
            'return_url': 'https://www.milove.com/',  # just put in
            'cancel_url': 'https://www.milove.com/'  # but we don't use it
        },
        'payer': {
            'payment_method': 'paypal'
        },
        'transactions': [
            {
                'amount': {
                    'total': '%.2f' % amount,
                    'currency': 'USD',
                },
            }
        ]
    })
    if paypal_payment.create():
        payment.vendor_payment_id = paypal_payment.id
        payment.extra_info = eval(str(paypal_payment))
        payment.status = Payment.STATUS_PENDING
    else:
        raise PaymentFailed


@pay_with(PaymentMethod.CREDIT_CARD)
def _pay_with_credit_card(payment, method_obj: PaymentMethod, amount):
    if not method_obj:
        raise PaymentFailed

    import stripe
    try:
        amount_in_cent = int(amount * 100)
        charge = stripe.Charge.create(
            amount=amount_in_cent,
            currency='usd',
            customer=method_obj.secret['customer_id'],
        )
        payment.vendor_payment_id = charge['id']
        payment.extra_info = charge
        if charge.get('paid'):
            payment.status = Payment.STATUS_SUCCEEDED
    except (stripe.error.InvalidRequestError,
            stripe.error.CardError):
        raise PaymentFailed
