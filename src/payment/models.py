import uuid

from django.db import models
from django.utils import timezone

from src.users.models import User
from src.basket.models import Basket, ClosedBasket, ClosedBasketDetail
from src.business.models import Business
from src.config.celery import app


def get_instance_values(instance):
    kwargs = instance.__dict__.copy()
    remove_keys = ("_state", "id", "slug")
    for key in remove_keys:
        del kwargs[key]
    return kwargs


# @app.task(name="payment.payment_done")
def payment_done(closed_basket_id):
    closed_basket = ClosedBasket.objects.get(id=closed_basket_id)
    # Closed Basket Detail fields
    for product in closed_basket.product.all():
        line_coupon = product.line_coupon
        codes = line_coupon.productvalidationcode_set.filter(used=False, closed_basket__isnull=True).order_by("id")[
                0:product.count]
        for code in codes:
            code.closed_basket_id = closed_basket_id
            code.save()
        product.payment_price = line_coupon.price
        product.payment_offer_percent = line_coupon.offer_percent
        product.payment_price_with_offer = line_coupon.price_with_offer
        product.save()
        # Line Coupon sell_count adding
        line_coupon.sell_count += product.count
        line_coupon.save()
    # Closed Basket fields
    closed_basket.is_paid = True
    closed_basket.payment_datetime = timezone.now()
    closed_basket.save()


class Payment(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True, verbose_name="اسلاگ")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    basket = models.ForeignKey(ClosedBasket, on_delete=models.CASCADE, null=True, blank=True, verbose_name="سبد خرید")
    total_price = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل")
    total_price_with_offer = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل با تخفیف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"

        # task when payment created
        payment_done(closed_basket_id=self.basket_id)
        # set closed basket and price fields
        self.closed_basket_id = self.basket_id
        self.total_price = self.basket.total_price
        self.total_price_with_offer = self.basket.total_price_with_offer
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.basket}({self.user})"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"
