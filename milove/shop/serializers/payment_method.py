import stripe
import stripe.error
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions, status

from ..models.payment_method import *

__all__ = ['PaymentMethodSerializer', 'PaymentMethodAddSerializer']


class PaymentMethodSerializer(serializers.ModelSerializer):
    info = serializers.JSONField(read_only=True)

    class Meta:
        model = PaymentMethod
        exclude = ('user', 'secret')
        extra_kwargs = {
            'method': {
                'read_only': True
            }
        }

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


def is_json_object(value):
    if not isinstance(value, dict):
        raise serializers.ValidationError(
            _('This field must be a JSON object.'))


class PaymentMethodCheckFailed(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('Payment method failed to pass check.')


class PaymentMethodAddSerializer(PaymentMethodSerializer):
    data = serializers.JSONField(write_only=True, validators=[is_json_object])

    class Meta(PaymentMethodSerializer.Meta):
        exclude = ('secret',)
        extra_kwargs = {
            'user': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            },
            'name': {
                'required': False
            },
            'method': {
                'read_only': False
            }
        }

    def create(self, validated_data):
        if validated_data['method'] == PaymentMethod.CREDIT_CARD:
            token = validated_data['data'].get('token')
            try:
                assert token and isinstance(token, dict)
                assert token.get('type') == 'card'
                assert 'id' in token and isinstance(token['id'], str)
            except AssertionError:
                raise exceptions.ValidationError(detail={
                    'data': {
                        'token': [
                            _('Value of "%(field_name)s" '
                              'field is not valid.') % {
                                'field_name': 'token'}
                        ]
                    }
                })
            try:
                customer = stripe.Customer.create(source=token['id'])
                card = customer.get('sources', {}).get('data', [{}])[0]
                payment_method = PaymentMethod()
                payment_method.user = validated_data['user']
                if 'name' in validated_data:
                    payment_method.name = validated_data['name']
                else:
                    payment_method.name = card.get('brand')
                payment_method.method = validated_data['method']
                payment_method.info = {}
                for k in ('brand', 'country', 'exp_month', 'exp_year',
                          'funding', 'last4'):
                    if card.get(k):
                        payment_method.info[k] = card[k]
                payment_method.secret = {
                    'customer_id': customer.get('id')
                }
                payment_method.save()
                return payment_method
            except (stripe.error.InvalidRequestError,
                    stripe.error.CardError):
                raise PaymentMethodCheckFailed
