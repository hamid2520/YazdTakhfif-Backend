from django.db import models
from django.utils.text import slugify

from src.business.models import Business


class Category(models.Model):
    choices = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    )
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True)
    level = models.CharField(max_length=2, choices=choices, default="1")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({self.level})"


class Coupon(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    business = models.ForeignKey(to=Business, on_delete=models.CASCADE)
    category = models.ManyToManyField(to=Category)
    description = models.TextField(blank=True, null=True)
    terms_of_use = models.TextField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({self.business})"


class LineCouponDetail(models.Model):
    price = models.CharField(max_length=16)
    discount_percent = models.CharField(max_length=8, default=0)
    sell_count = models.CharField(max_length=8, default=0)

    def __str__(self):
        return self.price


class LineCoupon(models.Model):
    title = models.CharField(max_length=128)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE)
    detail = models.OneToOneField(to=LineCouponDetail, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.coupon}({self.title})"
