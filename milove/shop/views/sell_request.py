import django_filters.rest_framework
from django.db import transaction
from rest_framework import viewsets, mixins, status, exceptions
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.pagination import PageNumberPagination

from ..models.sell_request import *
from ..serializers.sell_request import *
from .. import rest_filters
from .helpers import validate_or_raise, PartialUpdateModelMixin

router = SimpleRouter()


class SellRequestViewSet(mixins.CreateModelMixin,
                         viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SellRequestSerializer

    def get_queryset(self):
        return SellRequest.objects.filter(user=self.request.user)


router.register('sell_requests', SellRequestViewSet, base_name='sell_request')
urlpatterns = router.urls
