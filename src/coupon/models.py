from datetime import timedelta, datetime

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from src.business.models import Business


class Category(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True)
    level = models.SmallIntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({self.level})"


class FAQ(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)

    def clean(self):
        if not self.category.level == 1:
            raise ValidationError({"category": "Category must be at 1 level!"})

    def __str__(self):
        return f"{self.title[0:15]}({self.category})"

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


class Coupon(models.Model):
    title = models.CharField(max_length=128)
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
    title = models.CharField(max_length=128)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)
    count = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    offer_percent = models.PositiveSmallIntegerField()
    final_price = models.PositiveIntegerField(blank=True, null=True)
    bought_count = models.PositiveIntegerField(blank=True, default=0)
    rate = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(10), ])

    def validate_unique(self, exclude=None):
        if self.is_main:
            lines = LineCoupon.objects.filter(coupon__id=self.coupon.id, is_main=True)
            if lines.exists():
                if not lines.first().id == self.id:
                    raise ValidationError({"is_main": "Only one line can be active!"})
        return super().validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.final_price = self.price - (self.price * (self.offer_percent / 100))
        self.full_clean(exclude=None, validate_unique=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.coupon}({self.title})"
