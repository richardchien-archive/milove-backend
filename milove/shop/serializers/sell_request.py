from rest_framework import serializers

from ..models.sell_request import *
from ..validators import validate_json_array

__all__ = ['SellRequestSenderAddressSerializer',
           'SellRequestSerializer', ]


class SellRequestSenderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellRequestSenderAddress
        exclude = ('id', 'sell_request')


class SellRequestSerializer(serializers.ModelSerializer):
    image_paths = serializers.JSONField(validators=[validate_json_array])
    sender_address = SellRequestSenderAddressSerializer(read_only=True)

    class Meta:
        model = SellRequest
        fields = '__all__'
        read_only_fields = ('created_dt', 'status',
                            'buy_back_valuation', 'sell_valuation',
                            'valuated_dt', 'sell_type')
        extra_kwargs = {
            'user': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            },
        }
