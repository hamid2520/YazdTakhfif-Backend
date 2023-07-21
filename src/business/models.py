from typing import Any

from django.db import models
from django.utils.text import slugify

from src.users.models import User


class BusinessDetail(models.Model):
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class Business(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    detail = models.OneToOneField(to=BusinessDetail, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return self.title.capitalize()
