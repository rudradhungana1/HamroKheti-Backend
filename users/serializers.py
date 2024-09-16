from rest_framework import serializers
from users.models import User, UserProfile, FarmerProfile, PartnerProfile


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class SuperUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_superuser(**validated_data)
        user.user_role = 'admin'
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']

    def get_email(self, obj):
        return obj.user.email

    def get_username(self, obj):
        return obj.user.username


class FarmerProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = FarmerProfile
        fields = '__all__'

    def get_email(self, obj):
        return obj.user.email


class PartnerProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    username= serializers.SerializerMethodField()
    class Meta:
        model = PartnerProfile
        fields = '__all__'

    def get_email(self, obj):
        return obj.user.email

    def get_username(self, obj):
        return obj.user.username