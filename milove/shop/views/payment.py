from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import list_route

from ..models.payment import *
from ..models.payment_method import PaymentMethod
from ..serializers.payment import *
from ..exceptions import PaymentFailed
from .helpers import validate_or_raise

router = SimpleRouter()


class PaymentForm(forms.Form):
    method = forms.ChoiceField(choices=((PaymentMethod.PAYPAL, ''),))
    vendor_payment_id = forms.CharField()


_field_required_for_method_msg = _('The "%(field_name)s" is required for '
                                   'payment method "%(payment_method)s".')


class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentAddSerializer
        return PaymentSerializer

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validate_or_raise(serializer)
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data,
                        status=status.HTTP_201_CREATED)

    @list_route(['POST'])
    def execute(self, request, **kwargs):
        """Execute a payment after user authorized it."""

        form = PaymentForm(request.data)
        validate_or_raise(form)
        payment = get_object_or_404(
            self.get_queryset(),
            status=Payment.STATUS_PENDING,
            method=form.cleaned_data['method'],
            vendor_payment_id=form.cleaned_data['vendor_payment_id']
        )

        if payment.method == PaymentMethod.PAYPAL:
            if 'payer_id' not in request.data \
                    or not isinstance(request.data['payer_id'], str):
                raise exceptions.ValidationError({
                    'payer_id': _field_required_for_method_msg % {
                        'field_name': 'payer_id',
                        'payment_method': payment.method
                    }
                })

            import paypalrestsdk as paypal
            try:
                paypal_payment = paypal.Payment.find(payment.vendor_payment_id)
                if paypal_payment.execute(
                        {'payer_id': request.data['payer_id']}):
                    payment.extra_info = eval(str(paypal_payment))
                    payment.status = Payment.STATUS_SUCCEEDED
                else:
                    payment.status = Payment.STATUS_FAILED
            except paypal.exceptions.ClientError:
                payment.status = Payment.STATUS_FAILED
                raise PaymentFailed
            finally:
                payment.save()

        return Response()

    @list_route(['POST'])
    def cancel(self, request, **kwargs):
        """Cancel a payment, when the user cancelled the auth window."""

        form = PaymentForm(request.data)
        validate_or_raise(form)
        payment = get_object_or_404(
            self.get_queryset(),
            status=Payment.STATUS_PENDING,
            method=form.cleaned_data['method'],
            vendor_payment_id=form.cleaned_data['vendor_payment_id']
        )

        payment.status = Payment.STATUS_CLOSED
        payment.save()
        return Response()


router.register('payments', PaymentViewSet, base_name='payment')

urlpatterns = router.urls
