from rest_framework import serializers
from .models import Product, Comment, Review, Reply


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    farmer_name = serializers.SerializerMethodField(read_only=True)
    farmer_profile = serializers.SerializerMethodField(read_only=True)
    farmer_phone = serializers.SerializerMethodField(read_only=True)
    farmer_email = serializers.SerializerMethodField(read_only=True)
    farmer_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_farmer_address(self, obj):
        return obj.user.farmer_profile.address

    def get_farmer_email(self, obj):
        return obj.user.email
    def get_farmer_phone(self,obj):
        return obj.user.farmer_profile.phone or ""

    def get_farmer_name(self, obj):
        farmer_profile = obj.user.farmer_profile
        return farmer_profile.full_name or ""

    def get_farmer_profile(self, obj):
        return obj.user.farmer_profile.profile_image or None

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Unit price must be a positive value.')
        return value

    def validate_quantity_available(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity available must be a positive integer.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    profile_image = serializers.SerializerMethodField(read_only=True)
    farmer = serializers.SerializerMethodField(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'product', 'text', 'created_at', 'profile_image', 'farmer', 'replies')

    read_only_fields = ['user', 'created_at']

    def get_farmer(self, obj):
        return obj.product.user.username

    def get_replies(self, obj):
        replies = Reply.objects.filter(comment=obj.id)
        return ReplySerializer(replies, many=True).data

    def get_profile_image(self, obj):
        profile_url = ''
        if obj.user.user_role == 'farmer':
            profile_url = obj.user.farmer_profile.profile_image
        elif obj.user.user_role == 'partner':
            profile_url = obj.user.partner_profile.profile_image
        elif obj.user.user_role == 'normal_user':
            profile_url = obj.user.profile.profile_image
        return profile_url


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'user', 'text', 'created_at', 'profile_image']
        read_only_fields = ['user', 'created_at']

    def get_profile_image(self, obj):
        profile_url = ''
        if obj.user.user_role == 'farmer':
            profile_url = obj.user.farmer_profile.profile_image
        elif obj.user.user_role == 'partner':
            profile_url = obj.user.partner_profile.profile_image
        elif obj.user.user_role == 'normal_user':
            profile_url = obj.user.profile.profile_image
        return profile_url


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ('id', 'user', 'product', 'rating_value', 'review', 'created_at')


class ReviewCheckSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
