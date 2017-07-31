from rest_framework import viewsets, status
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.order import *
from ..serializers.order import *
from .helpers import validate_or_raise

router = DefaultRouter()


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderAddSerializer
        return OrderSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        validate_or_raise(serializer)
        order = serializer.save()
        return Response(OrderSerializer(order).data,
                        status=status.HTTP_201_CREATED)

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


router.register('orders', OrderViewSet, base_name='order')

urlpatterns = router.urls
