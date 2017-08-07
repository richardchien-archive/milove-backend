from django import forms
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import list_route

from ..models.payment import *
from ..models.payment_method import PaymentMethod
from ..serializers.payment import *
from ..exceptions import PaymentFailed
from ..payment_funcs import get_payment_func
from .helpers import validate_or_raise

router = SimpleRouter()


class PaymentForm(forms.Form):
    method = forms.ChoiceField(choices=((PaymentMethod.PAYPAL, ''),))
    vendor_payment_id = forms.CharField()


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
    def execution(self, request, **kwargs):
        """Execute a payment after user authorized it."""

        form = PaymentForm(request.data)
        validate_or_raise(form)
        payment = get_object_or_404(
            self.get_queryset(),
            status=Payment.STATUS_PENDING,
            method=form.cleaned_data['method'],
            vendor_payment_id=form.cleaned_data['vendor_payment_id']
        )

        try:
            func = get_payment_func(payment.method, stage='execute')
            if not func:
                raise PaymentFailed
            func(payment=payment, request=request)
        except PaymentFailed:
            payment.status = Payment.STATUS_FAILED
            raise
        finally:
            # no matter what happened, save the payment
            payment.save()

        return Response(PaymentSerializer(payment).data)

    @list_route(['POST'])
    def cancellation(self, request, **kwargs):
        """Cancel a payment, when the user cancelled the auth window."""
        # TODO: 这个函数其实可以删除

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
