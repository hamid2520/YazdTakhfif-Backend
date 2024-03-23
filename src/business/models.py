from django.db import models
from django.utils.text import slugify

from src.users.models import User


class Business(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name="عنوان")
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True,
                            verbose_name="اسلاگ")
    admin = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="ادمین ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    phone_number = models.CharField(max_length=11, blank=True, verbose_name="شماره تماس")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return self.title.capitalize()

    class Meta:
        verbose_name = "کسب و کار"
        verbose_name_plural = "کسب و کار ها"


DepositStatus = [('درحال انتظار', 0), ("تسویه شده", 1), ("رد شده", 2)]


class DepositRequest(models.Model):
    requested_date = models.DateField(verbose_name='تاریخ درخواست شده')
    requested_price = models.IntegerField(verbose_name='مبلغ درخواست')
    status = models.IntegerField(default=0, null=True, blank=True, choices=DepositStatus, verbose_name='وضعیت')
    deposit_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تسویه')
    document = models.ImageField(null=True, blank=True, verbose_name='مستندات تسویه')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ارسال کننده')

    class Meta:
        verbose_name = "درخواست تسویه"
        verbose_name_plural = "درخواست های تسویه"
        ordering = ['-requested_date']


class CorporateRequest(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=24)
    description = models.CharField(max_length=512)
    field = models.CharField(max_length=255)

    class Meta:
        verbose_name = "درخواست همکاری"
        verbose_name_plural = "درخواست های همکاری"
