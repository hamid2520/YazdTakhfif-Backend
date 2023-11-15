import uuid

from django.db import models
from django.utils import timezone
from rest_framework import settings
from rest_framework.reverse import reverse_lazy

from src.basket.models import Basket
from src.users.models import User
from src.payment.models import Payment
from src.payment_gateway.utils import zarinpal


class Gateway(models.Model):
    GATEWAY_CHOICES = (
        ("BMI", "ملی"),
        ("SEP", "SEP"),
        ("ZARINPAL", "زرین پال"),
        ("IDPAY", "آیدی پی"),
        ("MELLAT", "ملت"),
        ("ZIBAL", "زیبال"),
        ("BAHAMTA", "با همتا"),
        ("PAYV1", "PAYV1"),
    )
    name = models.CharField(max_length=128, verbose_name="نام درگاه")
    gateway = models.CharField(max_length=10, choices=GATEWAY_CHOICES, verbose_name="نوع درگاه")
    # put merchant_id or anything else in data
    data = models.JSONField(default=dict, null=True, blank=True, verbose_name="اطلاعات درگاه",
                            help_text="اطلاعات درگاه مانند مرچنت آیدی و ... را در این قسمت قرار دهید!")
    active = models.BooleanField(default=False, verbose_name="فعال / غیرفعال")

    def __str__(self):
        return f"{self.name}({self.gateway})"

    class Meta:
        verbose_name = "درگاه پرداخت"
        verbose_name_plural = "درگاه های پرداخت"


class OnlinePayment(models.Model):
    STATUS_NEW = 1
    STATUS_WAITING = 2
    STATUS_SUCCESS = 3
    STATUS_NOT_SUCCESS = 4
    STATUS_CANCELED = 5
    STATUS_CHOICES = (
        (STATUS_NEW, 'جدید'),
        (STATUS_WAITING, 'انتظار'),
        (STATUS_SUCCESS, 'موفق'),
        (STATUS_NOT_SUCCESS, 'ناموفق'),
        (STATUS_CANCELED, 'لغو'),
    )

    FAILED_CODE_NO_ERROR = 'بدون خطا'
    FAILED_CODE_GOTO_GATEWAY = 'خطای انتقال به درگاه پرداخت'
    FAILED_CODE_PRE_CONFIRM = 'خطای پرداخت در درگاه'
    FAILED_CODE_POST_CONFIRM = 'خطای اعتبار سنجی پرداخت'
    FAILED_CODE_GATEWAY_CONNECTION = 'خطای ارتباط با درگاه پرداخت'
    FAILED_CODE_FINALIZE = 'خطای نهایی سازی پرداخت'
    FAILED_CODE_CHOICES = (
        (0, FAILED_CODE_NO_ERROR),
        (5, FAILED_CODE_GOTO_GATEWAY),
        (10, FAILED_CODE_PRE_CONFIRM),
        (15, FAILED_CODE_POST_CONFIRM),
        (20, FAILED_CODE_GATEWAY_CONNECTION),
        (30, FAILED_CODE_FINALIZE),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="کاربر")
    status = models.PositiveSmallIntegerField(default=STATUS_NEW, verbose_name='وضعیت', choices=STATUS_CHOICES)
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='توکن', editable=False)
    gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE, verbose_name="درگاه")
    # جواب هنگام ارسال به درگاه پرداخت
    extra_data = models.JSONField(default=dict, null=True, blank=True, verbose_name="دیتای ارسالی به درگاه")
    # جواب بعد پرداخت
    # {pre_confirm={}, post_confirm={}}
    response = models.JSONField(default=dict, null=True, blank=True, verbose_name="دیتای دریافتی از درگاه")
    ref_id = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="کد رهگیری خرید")
    payment = models.ForeignKey(Basket, on_delete=models.SET_NULL, null=True, verbose_name="سبد خرید پرداختی")
    paid_at = models.DateTimeField(null=True, blank=True, default=None, verbose_name="تاریخ پرداخت")

    def __str__(self):
        return f"{str(self.token)}({self.user})"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.status != self.STATUS_NEW:
            if self.status == self.STATUS_SUCCESS:
                self.paid_at = timezone.now()
            self.ref_id = self.response["post_confirm"]["RefID"]
        return super().save(force_insert, force_update, using,
                            update_fields)

    class Meta:
        verbose_name = "پرداخت های آنلاین"
        verbose_name_plural = "پرداخت های آنلاین"
