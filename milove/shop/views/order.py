from django.db import transaction
from rest_framework import viewsets, status, exceptions
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from ..models.order import *
from ..serializers.order import *
from .helpers import validate_or_raise, PartialUpdateModelMixin

router = SimpleRouter()


class OrderViewSet(PartialUpdateModelMixin,
                   viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

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

    @detail_route(methods=['PUT'])
    def cancellation(self, request, **_):
        order = self.get_object()
        if order.status not in (Order.STATUS_UNPAID, Order.STATUS_PAID,
                                Order.STATUS_CANCELLING,
                                Order.STATUS_CANCELLED):
            raise exceptions.PermissionDenied

        if order.status != Order.STATUS_CANCELLING:
            # not cancelling
            with transaction.atomic():
                if order.status == Order.STATUS_PAID:
                    # the order is paid, give the user a refund
                    request.user.info.balance \
                        += order.total_price - order.discount_amount
                    # TODO: 这里要换成加上 Order 所关联的成功的 Payment 的金额
                    request.user.info.save()
                order.status = Order.STATUS_CANCELLED
                order.save()
        return Response(self.get_serializer(order).data)

    @detail_route(methods=['PUT'])
    def receipt_confirmation(self, request, **_):
        order = self.get_object()
        if order.status not in (Order.STATUS_SHIPPING, Order.STATUS_DONE):
            raise exceptions.PermissionDenied

        order.status = Order.STATUS_DONE
        order.save()
        return Response(self.get_serializer(order).data)

    @detail_route(methods=['PUT', 'DELETE'])
    def return_request(self, request, **_):
        order = self.get_object()
        if order.status not in (Order.STATUS_DONE,
                                Order.STATUS_RETURN_REQUESTED):
            raise exceptions.PermissionDenied

        if request.method == 'PUT':
            order.status = Order.STATUS_RETURN_REQUESTED
        else:
            order.status = Order.STATUS_DONE
        order.save()
        return Response(self.get_serializer(order).data)


router.register('orders', OrderViewSet, base_name='order')

urlpatterns = router.urls
