from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

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
    user = models.ForeignKey(User, models.CASCADE, verbose_name='کسب و کار', null=True, blank=True)
    type = models.SmallIntegerField(verbose_name='نوع', choices=TYPE_CHOICES)
    status = models.SmallIntegerField(verbose_name='وضعیت', choices=STATUS_CHOICES, default=2)
    amount = models.BigIntegerField(verbose_name='مبلغ')
    final_amount = models.BigIntegerField(blank=True, default=0, verbose_name='مبلغ با احتساب پورسانت')
    price_without_offer = models.BigIntegerField(verbose_name='مبلغ بدون نخفیف', null=True, blank=True)
    datetime = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    customer = models.CharField(null=True, blank=True, max_length=150, verbose_name='خریدار')
    closed_basket = models.ForeignKey(ClosedBasket, models.CASCADE, verbose_name='سبد خرید', null=True, blank=True)
    line_coupon = models.ForeignKey(LineCoupon, models.CASCADE, verbose_name='لاین کوپن', null=True, blank=True)
    coupon = models.ForeignKey(Coupon, models.CASCADE, verbose_name='کوپن', null=True, blank=True)
    commission = models.PositiveIntegerField(default=0, verbose_name='پورسانت کل')

    def clean(self):
        if self.type == 2:
            deposit = Transaction.objects.filter(user_id=self.user.id, type=1, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
            deposit = deposit if deposit else 0
            withdraw = Transaction.objects.filter(user_id=self.user.id, type=2, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
            withdraw = withdraw if withdraw else 0
            if deposit < withdraw + self.amount:
                raise ValidationError({"amount": "موجودی کسب و کار جهت برداشت کافی نیست!"})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        if self.type == 1:
            self.final_amount = self.amount - self.commission
        elif self.type == 2:
            self.final_amount = self.amount
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f'{self.user}({self.type})'

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش ها"
