from django.db import models
from django.utils.text import slugify

from src.users.models import User


class Business(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name="عنوان")
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    admin = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="ادمین ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    phone_number = models.CharField(max_length=11, blank=True, verbose_name="شماره تماس")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return self.title.capitalize()

    class Meta:
        verbose_name = "کسب و کار"
        verbose_name_plural = "کسب و کار ها"
