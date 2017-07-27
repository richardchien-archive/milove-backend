from django.contrib.auth.models import User
from rest_framework import serializers

from .models import *

__all__ = ('BrandSerializer', 'ProductSerializer',
           'UserInfoSerializer', 'UserSerializer')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class ProductImageField(serializers.RelatedField):
        def to_internal_value(self, data):
            return super().to_internal_value(data)

        def to_representation(self, value):
            return value.image.name

    class CategorySerializer(serializers.ModelSerializer):
        fullname = serializers.CharField(source='__str__')

        class Meta:
            model = Category
            fields = '__all__'

    main_image = serializers.ImageField(use_url=False, read_only=True)
    images = ProductImageField(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        exclude = ('buy_back_price',)  # hide this field to users
        depth = 1


class UserInfoSerializer(serializers.ModelSerializer):
    contact = serializers.JSONField()

    class Meta:
        model = UserInfo
        exclude = ['user']
        read_only_fields = ('balance', 'point')


class UserSerializer(serializers.ModelSerializer):
    info = UserInfoSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'info')

    def update(self, instance: User, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        info = validated_data.get('info', None)
        if info:
            info_serializer = UserInfoSerializer(instance.info,
                                                 data=info, partial=True)
            if info_serializer.is_valid():
                info_serializer.save()
        instance.save()
        return instance
