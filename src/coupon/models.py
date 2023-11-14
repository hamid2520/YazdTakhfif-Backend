import uuid
import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# from src.basket.models import ClosedBasket
from src.business.models import Business
from src.users.models import User


class Category(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True)
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


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
    expire_date = models.DateTimeField(null=True, blank=True)
    category = models.ManyToManyField(to=Category)
    description = models.CharField(max_length=1000, blank=True, null=True)
    terms_of_use = models.TextField(blank=True, null=True)
    coupon_rate = models.DecimalField(blank=True, null=True, max_digits=2, decimal_places=1)
    rate_count = models.PositiveIntegerField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        if not self.expire_date:
            self.expire_date = timezone.now() + timedelta(days=10)
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def get_main_line_coupon(self):
        return self.linecoupon_set.filter(is_main=True).first()

    def __str__(self):
        return f"{self.title}({self.business})"

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"


class LineCoupon(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True)
    title = models.CharField(max_length=128)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)
    count = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    offer_percent = models.PositiveSmallIntegerField()
    price_with_offer = models.PositiveIntegerField(blank=True, null=True)
    sell_count = models.PositiveIntegerField(blank=True, default=0)

    def validate_unique(self, exclude=None):
        if self.is_main:
            lines = LineCoupon.objects.filter(coupon__id=self.coupon.id, is_main=True)
            if lines.exists():
                if not lines.first().id == self.id:
                    raise ValidationError({"is_main": "Only one line can be active!"})
        return super().validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        self.price_with_offer = self.price - (self.price * (self.offer_percent / 100))
        self.full_clean(exclude=None, validate_unique=True)
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.coupon}({self.title})"

    class Meta:
        verbose_name = "Line Coupon"
        verbose_name_plural = "Line Coupons"


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5), ])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        detail = self.coupon.rate_set.all().aggregate(Avg("rate"), Count("id"))
        self.coupon.coupon_rate = detail["rate__avg"]
        self.coupon.rate_count = detail["id__count"]
        self.coupon.save()
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.coupon}({self.user})"

    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    parent = models.ForeignKey("Comment", on_delete=models.CASCADE, blank=True, null=True)
    text = models.CharField(max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False, verbose_name="تایید شده / نشده")

    def __str__(self):
        return f"{self.coupon}({self.user})-is sub comment({bool(self.parent)})"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
