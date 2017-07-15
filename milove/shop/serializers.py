from rest_framework import serializers

from . import models


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True)

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
