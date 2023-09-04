import uuid

from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from src.users.models import User
from src.coupon.models import LineCoupon


class BasketDetail(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True)
    line_coupon = models.ForeignKey(LineCoupon, on_delete=models.DO_NOTHING)
    count = models.PositiveSmallIntegerField()
    payment_price = models.PositiveIntegerField(blank=True, null=True)
    payment_offer_percent = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(100), ])
    payment_price_with_offer = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.PositiveIntegerField(blank=True, null=True)
    total_price_with_offer = models.PositiveIntegerField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        if self.payment_price:
            self.total_price = self.payment_price * self.count
            self.total_price_with_offer = self.payment_price_with_offer * self.count
        else:
            self.total_price = self.line_coupon.price * self.count
            self.total_price_with_offer = self.line_coupon.price_with_offer * self.count
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.line_coupon}({self.id})"

    class Meta:
        verbose_name = "Basket Detail"
        verbose_name_plural = "Basket Details"


class Basket(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True)
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
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        if not self.is_paid:
            self.total_price = self.product.all().aggregate(Sum("total_price"))["total_price__sum"]
            self.total_price_with_offer = self.product.all().aggregate(Sum("total_price_with_offer"))[
                "total_price_with_offer__sum"]
            self.total_offer_percent = 100 - (self.total_price_with_offer * 100 / self.total_price)
        # build user,modify product for validate_unique, count calculating
        super().save(force_insert, force_update, using, update_fields)
        self.count = self.product.all().count()
        self.full_clean()
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.user}({self.id})"

    class Meta:
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"
