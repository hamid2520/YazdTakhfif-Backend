from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator

from src.business.models import Business


class Offer(models.Model):
    offer_code = models.CharField(max_length=16, unique=True, db_index=True, verbose_name="کد تخفیف")
    percent = models.PositiveIntegerField(validators=[MaxValueValidator(100), ], verbose_name="درصد تخفیف")
    start_date = models.DateTimeField(default=timezone.now, blank=True, verbose_name="تاریخ شروع")
    expire_date = models.DateTimeField(verbose_name="تاریخ پایان")
    limited_businesses = models.ManyToManyField(to=Business, blank=True, verbose_name="کسب و کار ها")
    maximum_offer_price = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر مقدار تخفیف")

    def __str__(self):
        return f"{self.offer_code}({self.percent})"

    class Meta:
        verbose_name = "کد تخفیف سبد خرید"
        verbose_name_plural = "کد تخفیف های سبد خرید"
