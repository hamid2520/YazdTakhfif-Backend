from django.db import models
from src.business.models import Business


class Category(models.Model):
    choices = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    )
    title = models.CharField(max_length=128)
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True)
    level = models.CharField(max_length=2, choices=choices, default="1")

    def __str__(self):
        return f"{self.title}({self.level})"


class Coupon(models.Model):
    title = models.CharField(max_length=128)
    business = models.ForeignKey(to=Business, on_delete=models.CASCADE)
    category = models.ManyToManyField(to=Category)

    def __str__(self):
        return f"{self.title}({self.business})"


class LineCouponDetail(models.Model):
    price = models.CharField(max_length=128)

    def __str__(self):
        return self.price


class LineCoupon(models.Model):
    title = models.CharField(max_length=128)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE)
    detail = models.OneToOneField(to=LineCouponDetail, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.coupon}({self.title})"
