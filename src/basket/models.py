import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from src.users.models import User
from src.coupon.models import LineCoupon


class BasketDetail(models.Model):
    slug = models.SlugField(db_index=True, blank=True, default=uuid.uuid4, editable=False, unique=True)
    line_coupon = models.ForeignKey(LineCoupon, on_delete=models.DO_NOTHING)
    count = models.PositiveSmallIntegerField(default=1)
    payment_price = models.PositiveIntegerField(blank=True, null=True)
    payment_offer_percent = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(100), ])
    payment_price_with_offer = models.PositiveIntegerField(blank=True, null=True)
    final_price = models.PositiveIntegerField(blank=True, null=True)
    final_price_with_offer = models.PositiveIntegerField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        basket_detail = BasketDetail.objects.filter(id=self.id)
        if not basket_detail.exists():
            self.slug = f"{self.__class__.__name__.lower()}-{self.slug}"
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.line_coupon}({self.id})"

    class Meta:
        verbose_name = "Basket Detail"
        verbose_name_plural = "Basket Details"


class Basket(models.Model):
    slug = models.SlugField(db_index=True, blank=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(BasketDetail, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_datetime = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    count = models.PositiveSmallIntegerField(blank=True, default=0)
    total_price = models.PositiveIntegerField(blank=True, null=True)
    total_offer_percent = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(100), ])
    total_price_with_offer = models.PositiveIntegerField(blank=True, null=True)

    def validate_unique(self, exclude=None):
        if not self.is_paid:
            baskets = Basket.objects.filter(user=self.user, is_paid=False)
            if baskets.exists():
                if baskets.first() != self:
                    raise ValidationError({"is_paid": "Only one basket can be not paid!"})
        return super().validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        basket = Basket.objects.filter(id=self.id)
        if not basket.exists():
            self.slug = f"{self.__class__.__name__.lower()}-{self.slug}"
        self.full_clean()
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.user}({self.id})"

    class Meta:
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"
