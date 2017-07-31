from rest_framework import viewsets, mixins
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated

from ..models.payment_method import *
from ..serializers.payment_method import *
from .helpers import PartialUpdateModelMixin

router = SimpleRouter()


class PaymentMethodViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           PartialUpdateModelMixin,
                           viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentMethodAddSerializer
        return PaymentMethodSerializer


router.register('payment_methods', PaymentMethodViewSet,
                base_name='payment_method')

urlpatterns = router.urls
