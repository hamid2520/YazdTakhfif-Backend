from django.db import models
from src.basket.models import ClosedBasket
from src.coupon.models import LineCoupon, Coupon

from src.users.models import User


class Transaction(models.Model):
    TYPE_DEPOSIT_COMMISSION = 1
    TYPE_WITHDRAW_COMMISSION = 2
    TYPE_CHOICES = (
        (TYPE_DEPOSIT_COMMISSION, 'واریز'),
        (TYPE_WITHDRAW_COMMISSION, 'برداشت'),
    )

    STATUS_CHOICES = (
        (1, 'در انتظار تایید'),
        (2, 'موفق'),
        (3, 'ناموفق')
    )
    user = models.ForeignKey(User, models.CASCADE, verbose_name='کاربر', null=True, blank=True)
    type = models.SmallIntegerField(verbose_name='نوع', choices=TYPE_CHOICES)
    status = models.SmallIntegerField(verbose_name='وضعیت', choices=STATUS_CHOICES, default=1)
    amount = models.BigIntegerField(verbose_name='مبلغ')
    price_with_out_offer = models.BigIntegerField(verbose_name='مبلغ بدون نخفیف', null=True, blank=True)
    datetime = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    customer = models.CharField(null=True, blank=True, max_length=150)
    closed_basket = models.ForeignKey(ClosedBasket, models.CASCADE, verbose_name='سبد خرید', null=True, blank=True)
    line_coupon = models.ForeignKey(LineCoupon, models.CASCADE, verbose_name='لاین کوپن', null=True, blank=True)
    coupon = models.ForeignKey(Coupon, models.CASCADE, verbose_name='کوپن', null=True, blank=True)

    def __str__(self):
        return 'from:{} to:{} amount:{}'

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش ها"
