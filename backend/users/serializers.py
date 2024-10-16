import re
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True},}

    def validate_username(self, username):
        if not re.match('^[\w.@+-]+\Z', username):
            message = 'Invalid username!'
            raise serializers.ValidationError(message)
        return username

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)