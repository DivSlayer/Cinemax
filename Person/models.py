from django.db import models

from Person.values import get_person_root
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


def get_person_path(person, filename):
    return get_person_root(person, 'image.jpg')


class Person(models.Model):
    imdb_id = models.CharField(max_length=50)
    slug = models.SlugField(max_length=300, blank=True, null=True)
    name = models.CharField(max_length=100)
    img = models.FileField(upload_to=get_person_path)
    height = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.CharField(max_length=50, null=True, blank=True)
    age = models.CharField(max_length=10, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}-{self.imdb_id}"

    # class Meta:
    #     ordering = ('name',)


@receiver(pre_save, sender=Person)
def my_callback(sender, instance, *args, **kwargs):
    # instance.name = " ".join([str(word).capitalize() for word in instance.name.split(" ")])
    instance.slug = slugify(instance.name)
    instance.url = f"/person/{slugify(instance.name)}"
