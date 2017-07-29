from rest_framework import serializers

from ..models.address import *

__all__ = ['AddressSerializer']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            }
        }
