from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from .models import Subscriptions, User


class CustomUserCreateSerializer(UserCreateSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('avatar',)


class UserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = DjoserUserSerializer.Meta.fields + ('avatar', 'is_subscribed')

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=request.user, author=user
        ).exists()

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
