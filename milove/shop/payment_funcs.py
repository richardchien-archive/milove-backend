from functools import wraps
from collections import defaultdict

from django.conf import settings
from django.db import transaction

from .models.payment import Payment
from .models.payment_method import PaymentMethod
from .exceptions import PaymentFailed

_payment_funcs = defaultdict(dict)


def get_payment_func(method_name, stage='create'):
    return _payment_funcs[stage].get(method_name)


def register(method_name, stage='create'):
    """
    Decorate a function as the payment function of a given payment method.

    If the stage is "create",
    the function should receive these keyword arguments:
    - payment: a Payment object
    - method_obj: a PaymentMethod object, or None
    - amount: amount that should be charged, in USD

    If the state is "execute",
    - payment: a Payment object
    - request: the current request object

    The function should process the payment and change "payment" object
    if needed (especially the "status" and "vendor_payment_id" attributes),
    without need to call "save()" on it.

    If anything wrong happened while creating payment, raise PaymentFailed.

    :param method_name: payment method name
    :param stage: the payment processing stage, "create" or "execute"
    """

    def decorator(func):
        _payment_funcs[stage][method_name] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def charge_balance_and_point(payment):
    user = payment.order.user

    point_to_use = settings.POINT_TO_AMOUNT_REVERSE(
        payment.amount_from_point
    )
    if user.info.point >= point_to_use:
        with transaction.atomic():
            user.info.point -= point_to_use
            user.info.save()
            payment.paid_point = point_to_use
            payment.save()
    else:
        raise PaymentFailed

    balance_to_use = payment.amount_from_balance
    if user.info.balance >= balance_to_use:
        with transaction.atomic():
            user.info.balance -= balance_to_use
            user.info.save()
            payment.paid_amount_from_balance = balance_to_use
            payment.save()
    else:
        raise PaymentFailed


@register(PaymentMethod.CREDIT_CARD, stage='create')
def pay_with_credit_card(payment, method_obj: PaymentMethod, amount):
    if not method_obj:
        raise PaymentFailed

    charge_balance_and_point(payment)

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

    if payment.status != Payment.STATUS_SUCCEEDED:
        raise PaymentFailed


@register(PaymentMethod.PAYPAL, stage='create')
def pay_with_paypal(payment, amount, **kwargs):
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
        # this is safe, trust me, it's just a dict
        payment.extra_info = eval(str(paypal_payment))
        payment.status = Payment.STATUS_PENDING
    else:
        raise PaymentFailed


@register(PaymentMethod.PAYPAL, stage='execute')
def pay_with_paypal_execute(payment, request):
    if 'payer_id' not in request.data \
            or not isinstance(request.data['payer_id'], str):
        raise PaymentFailed

    charge_balance_and_point(payment)

    import paypalrestsdk as paypal
    try:
        paypal_payment = paypal.Payment.find(payment.vendor_payment_id)
        if paypal_payment.execute(
                {'payer_id': request.data['payer_id']}):
            payment.extra_info = eval(str(paypal_payment))
            payment.status = Payment.STATUS_SUCCEEDED
        else:
            raise PaymentFailed
    except paypal.exceptions.ClientError:
        raise PaymentFailed

    if payment.status != Payment.STATUS_SUCCEEDED:
        raise PaymentFailed
