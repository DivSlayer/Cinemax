from rest_framework import serializers

from Category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['en_title', 'fa_title', 'icon']
