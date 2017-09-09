import django_filters.rest_framework
from django.db import transaction
from rest_framework import viewsets, status, exceptions
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.pagination import PageNumberPagination

from ..models.order import *
from ..models.payment import Payment
from ..serializers.order import *
from .. import rest_filters
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

    class Pagination(PageNumberPagination):
        page_size = 15
        page_query_param = 'page_size'
        max_page_size = 30

    class Filter(django_filters.rest_framework.FilterSet):
        created_dt = django_filters.rest_framework.DateFromToRangeFilter()
        status = rest_filters.CommaSplitListFilter()
        status_not = rest_filters.CommaSplitListFilter(name='status',
                                                       exclude=True)

        class Meta:
            model = Order
            fields = ('created_dt', 'status', 'status_not')

    pagination_class = Pagination
    filter_class = Filter
    ordering = ('-created_dt',)
    search_fields = ('items__product__brand__name', 'items__product__name',
                     'items__product__style', 'items__product__size',
                     'items__product__categories__name')

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        validate_or_raise(serializer)
        order = serializer.save()
        return Response(OrderSerializer(order).data,
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['GET'])
    def status_transitions(self, request, **kwargs):
        order = self.get_object()
        needed_statuses = (
            Order.STATUS_CLOSED, Order.STATUS_CANCELLED,
            Order.STATUS_PAID, Order.STATUS_SHIPPING, Order.STATUS_DONE
        )
        result = {
            'created_dt': order.created_dt
        }
        result.update(dict.fromkeys([x + '_dt' for x in needed_statuses]))
        for trans in order.status_transitions.order_by('happened_dt'):
            if trans.dst_status in needed_statuses:
                result[trans.dst_status + '_dt'] = trans.happened_dt

        return Response(result)

    @detail_route(methods=['PUT'])
    def cancellation(self, request, **kwargs):
        order = self.get_object()
        if not is_status_transition_allowed(order.status,
                                            Order.STATUS_CANCELLED):
            raise exceptions.PermissionDenied

        if order.status != Order.STATUS_CANCELLING:
            # not cancelling
            with transaction.atomic():
                if order.status == Order.STATUS_PAID:
                    # the order is paid, give the user a refund
                    payment = order.payments.filter(
                        status=Payment.STATUS_SUCCEEDED).first()
                    if payment:
                        request.user.info.increase_point(payment.paid_point)
                        request.user.info.increase_balance(
                            payment.amount - payment.amount_from_point)
                order.status = Order.STATUS_CANCELLED
                order.save()

        return Response(self.get_serializer(order).data)

    @detail_route(methods=['PUT'])
    def receipt_confirmation(self, request, **kwargs):
        order = self.get_object()
        if not is_status_transition_allowed(order.status, Order.STATUS_DONE):
            raise exceptions.PermissionDenied

        order.status = Order.STATUS_DONE
        order.save()
        return Response(self.get_serializer(order).data)

    @detail_route(methods=['PUT', 'DELETE'])
    def return_request(self, request, **kwargs):
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
