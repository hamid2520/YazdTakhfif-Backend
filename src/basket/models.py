from django.db import models
from django.core.validators import MinValueValidator

from src.users.models import User
from src.coupon.models import LineCoupon


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}({self.user})"

    class Meta:
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"


class BasketDetail(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    line_coupon = models.ForeignKey(LineCoupon, on_delete=models.DO_NOTHING)
    count = models.SmallIntegerField(validators=MinValueValidator(1))

    def __str__(self):
        return f"{self.line_coupon}({self.basket})"

    class Meta:
        verbose_name = "Basket Detail"
        verbose_name_plural = "Basket Details"
