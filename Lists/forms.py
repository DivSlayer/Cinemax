from django import forms

from Lists.models import Item, List


class CreateListItem(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["title", "details", "status", "done", "color", "priority"]


class CreateList(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "en_name", "icon", "status", "done", "color"]
