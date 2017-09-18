from collections import Iterable

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ..models.sell_request import *
from ..validators import validate_json_array, validate_files_exist

__all__ = ['SellRequestSenderAddressSerializer',
           'SellRequestSerializer', ]


class SellRequestSenderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellRequestSenderAddress
        exclude = ('id', 'sell_request')


def validate_uploaded_files(value):
    if not isinstance(value, Iterable):
        return
    for name in value:
        if not name.startswith('uploads/'):
            raise ValidationError(_('File %(name)s is not valid.'),
                                  params={'name': name})


class SellRequestSerializer(serializers.ModelSerializer):
    image_paths = serializers.JSONField(
        validators=[validate_json_array,
                    validate_uploaded_files,
                    validate_files_exist]
    )
    sender_address = SellRequestSenderAddressSerializer(read_only=True)
    shipping_label = serializers.FileField(use_url=False, read_only=True)

    class Meta:
        model = SellRequest
        exclude = ('user',)
        read_only_fields = ('created_dt', 'status', 'denied_reason',
                            'buy_back_valuation', 'sell_valuation',
                            'valuated_dt', 'sell_type',
                            'express_company', 'tracking_number',
                            'done_dt')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
