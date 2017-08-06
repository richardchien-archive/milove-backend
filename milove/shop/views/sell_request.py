import django_filters.rest_framework
from django.db import transaction
from django import forms
from rest_framework import viewsets, mixins, status, exceptions
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.pagination import PageNumberPagination

from ..models.sell_request import *
from ..serializers.sell_request import *
from .. import rest_filters
from .helpers import validate_or_raise

router = SimpleRouter()


class SellRequestDecisionForm(forms.Form):
    sell_type = forms.ChoiceField(choices=SellRequest.SELL_TYPES)


class SellRequestViewSet(mixins.CreateModelMixin,
                         viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SellRequestSerializer

    def get_queryset(self):
        return SellRequest.objects.filter(user=self.request.user)

    @detail_route(methods=['PUT'])
    def cancellation(self, request, **kwargs):
        sell_req = self.get_object()
        if not is_status_transition_allowed(sell_req.status,
                                            SellRequest.STATUS_CANCELLED):
            raise exceptions.PermissionDenied

        sell_req.status = SellRequest.STATUS_CANCELLED
        sell_req.save()
        return Response(self.get_serializer(sell_req).data)

    @detail_route(methods=['PUT'])
    def decision(self, request, **kwargs):
        sell_req = self.get_object()
        if not is_status_transition_allowed(sell_req.status,
                                            SellRequest.STATUS_DECIDED):
            raise exceptions.PermissionDenied

        form = SellRequestDecisionForm(request.data)
        validate_or_raise(form)

        sell_req.sell_type = form.cleaned_data['sell_type']
        sell_req.status = SellRequest.STATUS_DECIDED
        sell_req.save()
        return Response(self.get_serializer(sell_req).data)


router.register('sell_requests', SellRequestViewSet, base_name='sell_request')

urlpatterns = router.urls
