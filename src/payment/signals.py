from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Payment
from ..basket.models import Basket


@receiver(post_save, sender=Payment)
def basket_remover(sender, **kwargs):
    basket: Basket = kwargs["instance"].basket
    basket.delete()
