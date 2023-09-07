from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from .models import Basket


@receiver(m2m_changed, sender=Basket.product.through)
def basket_products_price_updater(sender, **kwargs):
    basket: Basket = kwargs["instance"]
    basket.count = basket.product.all().count()
    if not basket.is_paid:
        basket.total_price = basket.product.all().aggregate(Sum("total_price"))["total_price__sum"] or 0
        basket.total_price_with_offer = basket.product.all().aggregate(Sum("total_price_with_offer"))[
                                            "total_price_with_offer__sum"] or 0

        if basket.total_price:
            basket.total_offer_percent = (100 - (basket.total_price_with_offer * 100 / basket.total_price))
        else:
            basket.total_offer_percent = 0
    basket.save()
