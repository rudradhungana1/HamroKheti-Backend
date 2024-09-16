from rest_framework import serializers

from users.serializers import UserSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)
