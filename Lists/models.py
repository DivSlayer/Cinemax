from django.db import models

from Utility.views import get_uuid


# Create your models here.
class List(models.Model):
    uuid = models.CharField(max_length=10, default=get_uuid, unique=True)
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=300, null=True, blank=True)
    en_name = models.CharField(max_length=200, null=True, blank=True)
    published_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    status = models.CharField(
        max_length=500,
        default="در حال انتظار",
        null=True,
        blank=True,
    )
    done = models.BooleanField(default=False)
    color = models.CharField(max_length=100, default="#ff9900")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("-done",)


class Item(models.Model):
    STATUS_CHOICES = (
        ("1", "بالا"),
        ("2", "معمولی"),
        ("3", "پایین"),
    )
    uuid = models.CharField(max_length=10, default=get_uuid, unique=True)
    belong = models.ForeignKey(List, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=500, default="در حال انتظار", null=True, blank=True
    )
    done = models.BooleanField(default=False)
    color = models.CharField(max_length=100, default="#ff9900")
    priority = models.CharField(choices=STATUS_CHOICES, max_length=200, default="2")
    published_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self) -> str:
        return self.title
