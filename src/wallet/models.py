from django.db import models

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
    datetime = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    buyer_phone = models.CharField(null=True, blank=True, max_length=11)

    def __str__(self):
        return 'from:{} to:{} amount:{}'
