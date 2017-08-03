from rest_framework import exceptions, status

from django.utils.translation import ugettext_lazy as _


class PaymentMethodCheckFailed(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('Payment method failed to pass check.')


class PaymentFailed(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('The payment is failed.')
