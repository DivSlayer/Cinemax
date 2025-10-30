from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from Utility.views import get_uuid


class Plan(models.Model):
    uuid = models.CharField(max_length=10, default=get_uuid, unique=True)
    title = models.CharField(max_length=100)
    play_available = models.BooleanField(default=False)
    download_available = models.BooleanField(default=False)
    duration = models.IntegerField()
    price = models.CharField(max_length=50)
    icon = models.CharField(max_length=300, null=True, blank=True)
    color = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.title


class MyAccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have passwords")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    plan = models.ForeignKey(Plan, on_delete=models.DO_NOTHING, blank=True, null=True)
    purchase_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    USERNAME_FIELD = "email"
    objects = MyAccountManager()

    def __str__(self) -> str:
        return self.email
