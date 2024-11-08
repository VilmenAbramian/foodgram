import base64
import re
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Subscriptions, User


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, username):
        if not re.match('^[\w.@+-]+\Z', username):
            raise serializers.ValidationError('Invalid username!')
        return username
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', 'avatar', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}, 'is_subscribed': {'read_only': True}}
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=request.user, author=obj).exists()
    
    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance 