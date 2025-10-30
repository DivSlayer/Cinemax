from django.db import models


class Category(models.Model):
    en_title = models.CharField(max_length=50)
    fa_title = models.CharField(max_length=50, blank=True, null=True)
    icon = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.fa_title
