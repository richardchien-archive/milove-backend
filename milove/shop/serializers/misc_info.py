from rest_framework import serializers

from ..models.misc_info import *

__all__ = ['MiscInfoSerializer']


class MiscInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiscInfo
        exclude = ('id',)
