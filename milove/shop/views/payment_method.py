from rest_framework.viewsets import ReadOnlyModelViewSet, mixins
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated

from ..models.payment_method import *
from ..serializers.payment_method import *

router = DefaultRouter()


class PaymentMethodViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           ReadOnlyModelViewSet):
    serializer_class = PaymentMethodSerializer
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
