from rest_framework import serializers

from Tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["en_title", "fa_title", "icon", "url"]
