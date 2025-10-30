from rest_framework import serializers
from django.contrib.auth import get_user_model

from Account.models import Plan

UserModel = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    plan = serializers.SerializerMethodField("get_plan")

    class Meta:
        model = UserModel
        fields = [
            "created_at",
            "email",
            "is_active",
            "last_login",
            "plan",
            "purchase_date",
        ]

    def get_plan(self, account):
        plan = account.plan
        return PlanSerializer(plan).data if plan else None
        
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"