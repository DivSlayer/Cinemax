from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Account.models import Account, Plan


class AccountAdmin(UserAdmin):
    list_display = ("email", "last_login", "created_at")
    search_fields = ("email",)


admin.site.register(Account)
admin.site.register(Plan)
