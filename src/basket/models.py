import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator

from src.users.models import User
from src.coupon.models import LineCoupon


# Basket Products
class BaseBasketDetail(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True, max_length=128)
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
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.line_coupon}({self.id})"

    class Meta:
        abstract = True


class BasketDetail(BaseBasketDetail):
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.payment_price:
            self.total_price = self.payment_price * self.count
            self.total_price_with_offer = self.payment_price_with_offer * self.count
        else:
            self.total_price = self.line_coupon.price * self.count
            self.total_price_with_offer = self.line_coupon.price_with_offer * self.count
        return super().save(force_insert, force_update, using,
                            update_fields)

    class Meta:
        verbose_name = "Basket Detail"
        verbose_name_plural = "Basket Details"


class ClosedBasketDetail(BaseBasketDetail):
    class Meta:
        verbose_name = "Closed Basket Detail"
        verbose_name_plural = "Closed Basket Details"


# Basket
class BaseBasket(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_datetime = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    count = models.PositiveSmallIntegerField(blank=True, null=True)
    total_price = models.PositiveIntegerField(blank=True, null=True)
    total_offer_percent = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(100), ])
    total_price_with_offer = models.PositiveIntegerField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.user}({self.id})"

    class Meta:
        abstract = True


class Basket(BaseBasket):
    product = models.ManyToManyField(BasketDetail, blank=True, null=True)

    def final_count_validation(self):
        errors = []
        if self.product.exists():
            for product in self.product.all():
                if product.count + product.line_coupon.sell_count > product.line_coupon.count:
                    errors.append(f"{product.line_coupon.title}`s count is more than available count!")
        else:
            errors.append("There is no products in basket!")
        if len(errors) > 0:
            return errors
        return None

    class Meta:
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"


class ClosedBasket(BaseBasket):
    product = models.ManyToManyField(ClosedBasketDetail, blank=True, null=True)

    class Meta:
        verbose_name = "ClosedBasket"
        verbose_name_plural = "ClosedBaskets"
