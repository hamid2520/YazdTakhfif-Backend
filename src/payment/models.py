import uuid

from django.db import models
from django.core.validators import MaxValueValidator
from django.utils import timezone

from src.business.models import Business
from src.users.models import User
from src.basket.models import Basket


def payment_done(instance, basket_id):
    basket = Basket.objects.get(id=basket_id)
    # Basket Detail fields
    for product in basket.product.all():
        line_coupon = product.line_coupon
        product.payment_price = line_coupon.price
        product.payment_offer_percent = line_coupon.offer_percent
        product.payment_price_with_offer = line_coupon.price_with_offer
        product.save()
        # Line Coupon sell_count adding
        line_coupon.sell_count += product.count
        line_coupon.save()
    # Basket fields
    basket.is_paid = True
    basket.payment_datetime = instance.created_at
    basket.save()


class Payment(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    total_price = models.PositiveIntegerField(blank=True, null=True)
    total_price_with_offer = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        # task when payment created
        payment_done(self, self.basket_id)
        self.total_price = self.basket.total_price
        self.total_price_with_offer = self.basket.total_price_with_offer
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.basket}({self.user})"

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"


class Offer(models.Model):
    offer_code = models.CharField(max_length=8, unique=True, db_index=True)
    percent = models.PositiveIntegerField(validators=[MaxValueValidator(100), ])
    Start_date = models.DateTimeField(default=timezone.now, blank=True)
    Expire_date = models.DateTimeField()
    Limited_businesses = models.ManyToManyField(to=Business, blank=True)
    maximum_offer_price = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.offer_code}({self.percent})"

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offer"
