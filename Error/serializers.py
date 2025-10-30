from rest_framework import serializers
from Error.models import Error


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = ["device", "message", "time"]
