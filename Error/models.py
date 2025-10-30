from datetime import datetime
from django.db import models


# Create your models here.
class Error(models.Model):
    message = models.TextField(blank=True)
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    device = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.device + " " + self.time.strftime("%d/%m/%Y, %H:%M:%S")
