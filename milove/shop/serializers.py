from rest_framework import serializers

from . import models


class ProductSerializer(serializers.ModelSerializer):
    class ProductImageField(serializers.RelatedField):
        def __init__(self, **kwargs):
            super().__init__(read_only=True, **kwargs)

        def to_internal_value(self, data):
            return super().to_internal_value(data)

        def to_representation(self, value):
            return value.image.name

    main_image = serializers.ImageField(use_url=False)
    images = ProductImageField(many=True)

    class Meta:
        model = models.Product
        fields = '__all__'
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    username = serializers.CharField(source='get_username')
    email = serializers.CharField(source='get_email')

    class Meta:
        model = models.UserInfo
        exclude = ['user']
