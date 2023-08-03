from rest_framework import serializers
from rest_framework.exceptions import NotFound

from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', )


class GetJWTTokenSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        if not User.objects.filter(email=data.get("email")).exists():
            raise NotFound("Ошибка: не верный email")
        if not User.objects.filter(
            password=data.get("password")
        ).exists():
            raise serializers.ValidationError(
                "Ошибка: не верный password"
            )
        return data
