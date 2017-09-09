from rest_framework import viewsets, mixins
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated

from ..serializers.withdrawal import *

router = SimpleRouter()


class WithdrawalViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = WithdrawalAddSerializer


router.register('withdrawals', WithdrawalViewSet, base_name='withdrawal')

urlpatterns = router.urls
