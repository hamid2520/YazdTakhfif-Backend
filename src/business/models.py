from django.db import models
from django.db.models import Sum
from django.utils.text import slugify
from rest_framework.exceptions import APIException, ValidationError

from src.users.models import User


class Business(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name="عنوان")
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True,
                            verbose_name="اسلاگ")
    admin = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="ادمین ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    phone_number = models.CharField(max_length=11, blank=True, verbose_name="شماره تماس")
    lat_map = models.DecimalField(max_digits=18, decimal_places=16, blank=True, null=True,
                                  verbose_name='عرض موقعیت مکانی')
    lang_map = models.DecimalField(max_digits=18, decimal_places=16, blank=True, null=True,
                                   verbose_name='طول موقعیت مکانی')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return self.title.capitalize()

    class Meta:
        verbose_name = "کسب و کار"
        verbose_name_plural = "کسب و کار ها"


DepositStatus = [(0, 'درحال انتظار'), (1, "تسویه شده"), (2, "رد شده")]


class DepositRequest(models.Model):
    requested_date = models.DateField(verbose_name='تاریخ درخواست شده')
    requested_price = models.IntegerField(verbose_name='مبلغ درخواست')
    status = models.IntegerField(default=0, null=True, blank=True, choices=DepositStatus, verbose_name='وضعیت')
    deposit_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تسویه')
    document = models.ImageField(null=True, blank=True, verbose_name='مستندات تسویه')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ارسال کننده')

    def save_base(self, raw=False, force_insert=False, force_update=False, using=None, update_fields=None):
        from src.wallet.models import Transaction
        deposit = Transaction.objects.filter(user_id=self.sender.id, type=1, status=2).aggregate(Sum("amount"))[
                      "amount__sum"] or 0
        already_requested = DepositRequest.objects.filter(sender=self.sender, status=0).aggregate(Sum("requested_price"))[
                                'requested_price__sum'] or 0
        withdraw = Transaction.objects.filter(user_id=self.sender.id, type=2, status=2).aggregate(Sum("amount"))[
                       "amount__sum"] or 0
        if deposit < withdraw + self.requested_price + already_requested:
            raise ValidationError({"requested_price": "موجودی کسب و کار جهت برداشت کافی نیست!"})
        super(DepositRequest, self).save_base()

    class Meta:
        verbose_name = "درخواست تسویه"
        verbose_name_plural = "درخواست های تسویه"
        ordering = ['-requested_date']


class CorporateRequest(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    phone_number = models.CharField(max_length=24, verbose_name='شماره موبایل')
    description = models.CharField(max_length=512, verbose_name='توضیحات')
    field = models.CharField(max_length=255, verbose_name='زمینه کاری')

    class Meta:
        verbose_name = "درخواست همکاری"
        verbose_name_plural = "درخواست های همکاری"
