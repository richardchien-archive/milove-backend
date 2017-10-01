from rest_framework import serializers

from ..models.product import *

__all__ = ['BrandSerializer', 'CategorySerializer',
           'AttachmentSerializer', 'ProductSerializer']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='__str__')
    simple_name = serializers.CharField()

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class ProductImageField(serializers.RelatedField):
        def to_internal_value(self, data):
            return super().to_internal_value(data)

        def to_representation(self, value):
            return value.image.name

    main_image = serializers.ImageField(use_url=False, read_only=True)
    images = ProductImageField(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    brief_info = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        exclude = ('buy_back_price',)  # hide this field to users
        depth = 1
