from rest_framework import viewsets
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated

from ..models.address import *
from ..serializers.address import *

router = SimpleRouter()


class AddressViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)


router.register('addresses', AddressViewSet, base_name='address')

urlpatterns = router.urls
