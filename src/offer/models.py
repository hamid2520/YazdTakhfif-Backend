from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator

from src.business.models import Business


class Offer(models.Model):
    offer_code = models.CharField(max_length=16, unique=True, db_index=True)
    percent = models.PositiveIntegerField(validators=[MaxValueValidator(100), ])
    start_date = models.DateTimeField(default=timezone.now, blank=True)
    expire_date = models.DateTimeField()
    limited_businesses = models.ManyToManyField(to=Business, blank=True)
    maximum_offer_price = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.offer_code}({self.percent})"

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offer"
