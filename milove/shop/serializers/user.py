from rest_framework import serializers
from rest_framework import exceptions

from ..models import *
from ..auth import User


class UserInfoSerializer(serializers.ModelSerializer):
    contact = serializers.JSONField()

    class Meta:
        model = UserInfo
        exclude = ['user']
        read_only_fields = ('balance', 'point')


class UserSerializer(serializers.ModelSerializer):
    info = UserInfoSerializer(required=False)

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_staff',
                   'groups', 'user_permissions')

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


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('old_password', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise exceptions.PermissionDenied
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
