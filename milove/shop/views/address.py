from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated

from ..models.address import *
from ..serializers.address import *

router = DefaultRouter()


class AddressViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        polyfill = {'user': self.request.user.pk}

        if 'data' in kwargs:
            data = dict(kwargs.pop('data'))
        elif len(args) > 1:
            data = dict(args[1])
            args = args[:1] + args[2:]
        else:
            data = None

        if data:
            data.update(polyfill)
            kwargs['data'] = data

        return super().get_serializer(*args, **kwargs)


router.register('addresses', AddressViewSet, base_name='address')

urlpatterns = router.urls
