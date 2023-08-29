from datetime import timedelta, datetime

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from src.business.models import Business


class Category(models.Model):
    title = models.CharField(max_length=128,unique=True)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True)
    level = models.SmallIntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({self.level})"


class Coupon(models.Model):
    title = models.CharField(max_length=128,unique=True)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    business = models.ForeignKey(to=Business, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(default=(datetime.now() + timedelta(days=10)), blank=True)
    category = models.ManyToManyField(to=Category)
    description = models.CharField(max_length=1000, blank=True, null=True)
    terms_of_use = models.TextField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({self.business})"


class LineCoupon(models.Model):
    title = models.CharField(max_length=128,unique=True)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)
    price = models.IntegerField(validators=[MinValueValidator(1), ])
    discount_percent = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    final_price = models.IntegerField(blank=True, null=True, )

    def validate_unique(self, exclude=None):
        if self.is_main:
            lines = LineCoupon.objects.filter(coupon=self.coupon, is_main=True)
            if lines.exists():
                if not lines.first() == self:
                    raise ValidationError({"is_main": "Only one line can be active!"})
        return super().validate_unique(exclude=None)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.final_price = (self.price * (100 - self.discount_percent))
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.coupon}({self.title})"
