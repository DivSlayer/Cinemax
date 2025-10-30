from django.db import models

# Create your models here.


class Country(models.Model):
    name = models.CharField(max_length=300)
    fa_name = models.CharField(max_length=300, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self) -> str:
        return self.name
