from rest_framework import serializers

from . import models


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
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
            model = models.Category
            fields = '__all__'

    main_image = serializers.ImageField(use_url=False, read_only=True)
    images = ProductImageField(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        exclude = ('buy_back_price',)  # hide this field to users
        depth = 1


class UserInfoSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    username = serializers.CharField(source='get_username', read_only=True)
    email = serializers.CharField(source='get_email', read_only=True)

    class Meta:
        model = models.UserInfo
        exclude = ['user']
