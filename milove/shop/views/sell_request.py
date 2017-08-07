import django_filters.rest_framework
from django.db import transaction
from django import forms
from rest_framework import viewsets, mixins, exceptions
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.pagination import PageNumberPagination

from ..models.sell_request import *
from ..models.address import Address
from ..serializers.sell_request import *
from .. import rest_filters
from .helpers import validate_or_raise

router = SimpleRouter()


class SellRequestDecisionForm(forms.Form):
    sell_type = forms.ChoiceField(choices=SellRequest.SELL_TYPES)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['sender_address'] = forms.ModelChoiceField(
            queryset=Address.objects.filter(user=user)
        )


class SellRequestViewSet(mixins.CreateModelMixin,
                         viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SellRequestSerializer

    def get_queryset(self):
        return SellRequest.objects.filter(user=self.request.user)

    class Pagination(PageNumberPagination):
        page_size = 15

    class Filter(django_filters.rest_framework.FilterSet):
        created_dt = django_filters.rest_framework.DateFromToRangeFilter()
        status = rest_filters.CommaSplitListFilter()
        valuated_dt = django_filters.rest_framework.DateFromToRangeFilter()
        sell_type = rest_filters.CommaSplitListFilter()

        class Meta:
            model = SellRequest
            fields = ('created_dt', 'status', 'valuated_dt', 'sell_type')

    pagination_class = Pagination
    filter_class = Filter
    ordering = ('-created_dt',)
    search_fields = ('brand', 'category', 'name', 'size', 'condition',
                     'purchase_year', 'attachments', 'description')

    @detail_route(methods=['PUT'])
    def cancellation(self, request, **kwargs):
        sell_req = self.get_object()
        if not is_status_transition_allowed(sell_req.status,
                                            SellRequest.STATUS_CANCELLED):
            raise exceptions.PermissionDenied

        sell_req.status = SellRequest.STATUS_CANCELLED
        sell_req.save()
        return Response(self.get_serializer(sell_req).data)

    @detail_route(methods=['POST'])
    def decision(self, request, **kwargs):
        sell_req = self.get_object()
        if not is_status_transition_allowed(sell_req.status,
                                            SellRequest.STATUS_DECIDED) \
                or sell_req.status == SellRequest.STATUS_DECIDED:
            raise exceptions.PermissionDenied

        form = SellRequestDecisionForm(request.data, user=request.user)
        validate_or_raise(form)

        with transaction.atomic():
            # create address first,
            # so that the notifization mail can access it
            address = form.cleaned_data['sender_address']
            SellRequestSenderAddress.objects.create(
                sell_request=sell_req,
                fullname=address.fullname,
                phone_number=address.phone_number,
                country=address.country,
                street_address=address.street_address,
                city=address.city,
                province=address.province,
                zip_code=address.zip_code
            )

            sell_req.sell_type = form.cleaned_data['sell_type']
            sell_req.status = SellRequest.STATUS_DECIDED
            sell_req.save()

        return Response(self.get_serializer(sell_req).data)


router.register('sell_requests', SellRequestViewSet, base_name='sell_request')

urlpatterns = router.urls
