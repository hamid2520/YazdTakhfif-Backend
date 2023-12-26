from re import S
from django.db import models, transaction, DatabaseError
from django.conf import settings
from rest_framework.serializers import ValidationError

from src.users.models import User


# from core.util.extend import raise_not_field_error


class Account(models.Model):
    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "حساب‌ ها"

    ACCOUNT_YAZD_TAKHFIF_COMMISSION_ID = 100
    ACCOUNT_YAZD_TAKHFIF_BANK1_ID = 101

    TYPE_COMMISSION = 1
    TYPE_CHARGE = 2
    TYPE_SETTLEMENT = 3
    TYPE_CHOICES = (
        (TYPE_COMMISSION, 'حساب پورسانت'),
        (TYPE_CHARGE, 'حساب شارژ'),
        (TYPE_SETTLEMENT, 'حساب تسویه'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='ضاحب حساب')
    balance = models.BigIntegerField(verbose_name='موجودی', default=0)
    type = models.SmallIntegerField(
        verbose_name='نوع', choices=TYPE_CHOICES)
    # برای حسابهای بدهکاری : وقتی پولی به این حساب واریز بشه موجودیش کسر میشه و وقتی ازش برداشت بشه ، موجودیش افزوده میشه.
    # مثل حساب پرداخت پورسانت یزدتخفیف که اول صفر هست و با پرداخت پورسانت به اعضا، موجودیش مثبت میشه و با تسویه اعضا، موجودیش کسر میشه
    debit = models.BooleanField(verbose_name='حساب بدهکاری', default=False)

    def __str__(self):
        return self.owner.get_full_name() if self.owner else str(self.pk)


class Transaction(models.Model):
    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ ها'

    TYPE_DEPOSIT_COMMISSION = 1
    TYPE_WITHDRAW_COMMISSION = 2
    TYPE_CHOICES = (
        (TYPE_DEPOSIT_COMMISSION, 'واریز'),
        (TYPE_WITHDRAW_COMMISSION, 'برداشت'),
    )

    STATUS_CHOICES = (
        (1, 'موفق'),
        (2, 'ناموفق'),
        (3,'در انتظار تایید')
    )
    type = models.SmallIntegerField(verbose_name='نوع', choices=TYPE_CHOICES)
    amount = models.BigIntegerField(verbose_name='مبلغ')
    datetime = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    status = models.SmallIntegerField(verbose_name='وضعیت', choices=STATUS_CHOICES)

    def __str__(self):
        return 'from:{} to:{} amount:{}'.format(
            self.from_account.owner.get_full_name(
            ) if self.from_account.owner else str(self.from_account.pk),
            self.to_account.owner.get_full_name(
            ) if self.to_account.owner else str(self.to_account.pk),
            str(self.amount),
        )

    def total_deposit(self, user):
        user_acc, created = Account.objects.get_or_create(
            owner=user,
            type=Account.TYPE_COMMISSION,
        )
        # account = Account.objects.filter(owner=user)
        deposit = Transaction.objects.filter(
            to_account=user_acc, type=Transaction.TYPE_DEPOSIT_COMMISSION)
        total = 0
        for item in deposit:
            total += item.amount
        return total

    def total_withdraw(self, user):
        user_acc, created = Account.objects.get_or_create(
            owner=user,
            type=Account.TYPE_COMMISSION,
        )
        # account = Account.objects.filter(owner=user)
        withdraw = Transaction.objects.filter(
            from_account=user_acc, type=Transaction.TYPE_WITHDRAW_COMMISSION)
        total = 0
        for item in withdraw:
            total += item.amount
        return total

    def count_deposit(self, user):
        user_acc, created = Account.objects.get_or_create(
            owner=user,
            type=Account.TYPE_COMMISSION,
        )
        # account = Account.objects.filter(owner=user)
        count = Transaction.objects.filter(
            to_account=user_acc, type=Transaction.TYPE_DEPOSIT_COMMISSION).count()
        return count

    @staticmethod
    def add_transaction(from_acc, to_acc, type, amount):
        try:
            with transaction.atomic():
                trans = Transaction.objects.create(
                    from_account=from_acc,
                    to_account=to_acc,
                    type=type,
                    amount=amount
                )

                if from_acc.debit:
                    from_acc.balance = from_acc.balance + amount
                else:
                    from_acc.balance = from_acc.balance - amount

                if to_acc.debit:
                    to_acc.balance = to_acc.balance - amount
                else:
                    to_acc.balance = to_acc.balance + amount

                from_acc.save()
                to_acc.save()

                Turnover.objects.create(
                    transaction=trans,
                    account=from_acc,
                    balance=from_acc.balance
                )
                Turnover.objects.create(
                    transaction=trans,
                    account=to_acc,
                    balance=to_acc.balance
                )
                return trans
        except BaseException as e:
            raise ValueError(str(e))


class Turnover(models.Model):
    class Meta:
        verbose_name = 'گردش حساب'
        verbose_name_plural = 'گردش حساب ها'

    transaction = models.ForeignKey(
        'wallet.Transaction', on_delete=models.CASCADE, verbose_name='تراکنش')
    account = models.ForeignKey(
        'wallet.Account', on_delete=models.CASCADE, verbose_name='حساب')
    balance = models.BigIntegerField(verbose_name='موجودی')

    def __str__(self):
        return self.account.owner.get_full_name() if self.account.owner else str(self.account.pk)


class RequestSettlement(models.Model):
    class Meta:
        verbose_name = 'درخواست تسویه'
        verbose_name_plural = 'درخواست های تسویه'

    STATUS_UNPAID = 1
    STATUS_WAITING = 2
    STATUS_PAID = 3
    STATUS_CHOICES = (
        (STATUS_UNPAID, 'پرداخت نشده'),
        (STATUS_WAITING, 'در انتظار تایید'),
        (STATUS_PAID, 'پرداخت شده'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    amount = models.BigIntegerField(verbose_name='مقدار درخواست')
    status = models.SmallIntegerField(verbose_name='وضعیت پرداخت', choices=STATUS_CHOICES)

    def __str__(self):
        return self.user.get_full_name()
