# news/serializers.py

from rest_framework import serializers
from .models import News, VegetableMarget


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class VegetableMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = VegetableMarget
        fields = '__all__'


class AddNewsSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = News
        fields = 'title', 'content', 'created_at', 'source'
