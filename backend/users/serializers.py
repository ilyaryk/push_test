from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        model = User
