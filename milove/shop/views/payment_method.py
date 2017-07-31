from rest_framework import viewsets, mixins
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.payment_method import *
from ..serializers.payment_method import *
from .helpers import validate_or_raise

router = SimpleRouter()


class PaymentMethodViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentMethodAddSerializer
        return PaymentMethodSerializer

    def partial_update(self, request, **_):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        validate_or_raise(serializer)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


router.register('payment_methods', PaymentMethodViewSet,
                base_name='payment_method')

urlpatterns = router.urls
