from rest_framework import serializers

from Lists.models import Item, List


class ListSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField("get_items")

    class Meta:
        model = List
        fields = [
            "name",
            "en_name",
            "icon",
            "status",
            "done",
            "color",
            "items",
        ]

    def get_items(self, list_ins):
        items = (
            Item.objects.filter(belong=list_ins).order_by("done").order_by("priority")
        )
        return ItemSerializer(items, many=True).data


class ItemSerializer(serializers.ModelSerializer):
    belong = serializers.SerializerMethodField("get_belong")

    class Meta:
        model = Item
        fields = [
            "uuid",
            "belong",
            "title",
            "details",
            "status",
            "done",
            "color",
            "priority",
        ]

    def get_belong(self, item):
        return item.belong.en_name
