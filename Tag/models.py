from django.db import models


# Create your models here.

class Tag(models.Model):
    en_title = models.CharField(max_length=300)
    fa_title = models.CharField(max_length=300)
    icon = models.CharField(max_length=300)
    url = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.fa_title
        
    class Meta:
        ordering = ('en_title',)
