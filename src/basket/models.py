import random
import string
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Count, Sum, Avg

from src.coupon.models import LineCoupon
from src.users.models import User


def generate_random_string(prefix="", length=8):
    characters = list(string.ascii_letters + string.digits)
    return prefix + "".join(random.choice(characters) for _ in range(length))


# Basket Products
class BaseBasketDetail(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True, max_length=128,
                            verbose_name="اسلاگ")
    line_coupon = models.ForeignKey(LineCoupon, on_delete=models.CASCADE, verbose_name="لاین کوپن")
    count = models.PositiveSmallIntegerField(verbose_name="تعداد")
    payment_price = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت تمام شده")
    payment_offer_percent = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(100), ],
                                                        verbose_name="تخفیف تمام شده")
    payment_price_with_offer = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت تمام شده با تخفیف")
    total_price = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل")
    total_price_with_offer = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل با تخفیف")

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
    def clean(self):
        super().clean()
        if (self.count + self.line_coupon.sell_count) > self.line_coupon.count:
            raise ValidationError({"count": "There is no more line coupons available!"})

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
        ordering = ['slug', ]
        verbose_name = "محصول سبد خرید"
        verbose_name_plural = "محصولات سبد خرید"


class ClosedBasketDetail(BaseBasketDetail):
    status_choices = (
        (1, "ایجاد شده"),
        (2, "تایید شده"),
        (3, "لغو شده"),
    )
    status = models.PositiveIntegerField(choices=status_choices, default=1, blank=True, verbose_name="وضعیت")

    class Meta:
        verbose_name = "محصول سبد خرید بسته شده"
        verbose_name_plural = "محصولات سبد خرید بسته شده"


# Basket
class BaseBasket(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True, verbose_name="اسلاگ")
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, verbose_name="کاربر")
    gifted = models.CharField(max_length=11, blank=True, null=True, verbose_name="هدیه به")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد سبد خرید")
    payment_datetime = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پرداخت سبد خرید")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده / نشده")
    count = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name="تعداد")
    total_price = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل")
    total_offer_percent = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(100), ],
                                                      verbose_name="تخفیف کل")
    total_price_with_offer = models.PositiveIntegerField(blank=True, default=0, verbose_name="قیمت کل با تخفیف")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.user}({self.id})"

    class Meta:
        abstract = True


class Basket(BaseBasket):
    product = models.ManyToManyField(BasketDetail, blank=True, null=True, verbose_name="محصولات")

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

    def update_basket(self):
        stats = self.product.all().aggregate(count=Avg("count"),
                                             total_price=Sum("total_price"),
                                             total_offer_percent=Sum("line_coupon__offer_percent"),
                                             total_price_with_offer=Sum("total_price_with_offer"))
        self.count = stats["count"]
        self.total_price = stats["total_price"]
        self.total_offer_percent = stats["total_offer_percent"]
        self.total_price_with_offer = stats["total_price_with_offer"]
        self.save()

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبد خرید ها"


class ClosedBasket(BaseBasket):
    status_choices = (
        (1, "ایجاد شده"),
        (2, "پرداخت شده"),
        (3, "تایید شده"),
        (4, "لغو شده"),
    )
    product = models.ManyToManyField(ClosedBasketDetail, blank=True, null=True, verbose_name="محصولات")
    status = models.PositiveIntegerField(choices=status_choices, default=2, blank=True, verbose_name="وضعیت")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.is_paid = True
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    class Meta:
        verbose_name = "سبد خرید بسته شده"
        verbose_name_plural = "سبد خرید های بسته شده"


class ProductValidationCode(models.Model):
    product = models.ForeignKey(LineCoupon, on_delete=models.CASCADE, verbose_name="لاین کوپن")
    code = models.CharField(max_length=128, db_index=True, unique=True, blank=True, default=generate_random_string,
                            verbose_name="کد تخفیف")
    used = models.BooleanField(default=False, verbose_name="استفاده شده / نشده")
    closed_basket = models.ForeignKey(ClosedBasket, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="سبد خرید بسته شده")

    def __str__(self):
        return f"{self.product.title}({self.pk})"

    class Meta:
        verbose_name = "کد تخفیف لاین کوپن"
        verbose_name_plural = "کد تخفیف های لاین کوپن"
