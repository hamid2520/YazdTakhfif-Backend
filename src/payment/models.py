import uuid

from django.db import models

from src.users.models import User
from src.basket.models import Basket


def payment_done(instance, basket_id):
    basket = Basket.objects.get(id=basket_id)
    # Basket Detail fields
    for product in basket.product.all():
        product.payment_price = product.line_coupon.price
        product.payment_offer_percent = product.line_coupon.offer_percent
        product.payment_price_with_offer = product.line_coupon.price_with_offer
        product.save()
        # Line Coupon sell_count adding
        product.line_coupon.sell_count += product.count
        product.line_coupon.save()
    # Basket fields
    basket.is_paid = True
    basket.payment_datetime = instance.created_at
    basket.save()
    instance.total_price = basket.total_price
    instance.total_price_with_offer = basket.total_price_with_offer


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
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.basket}({self.user})"

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
