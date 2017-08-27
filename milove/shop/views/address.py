from rest_framework import viewsets, exceptions
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

    def create(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs.count() >= 10:
            raise exceptions.PermissionDenied
        return super().create(request, *args, **kwargs)


router.register('addresses', AddressViewSet, base_name='address')

urlpatterns = router.urls
