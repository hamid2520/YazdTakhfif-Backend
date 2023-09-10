from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from .models import Basket, BasketDetail


@receiver(m2m_changed, sender=Basket.product.through)
def basket_products_price_updater(sender, **kwargs):
    basket: Basket = kwargs["instance"]
    if not basket.is_paid:
        basket.count = basket.product.all().aggregate(Sum("count"))["count__sum"]
        basket.count = basket.count if basket.count else 0
        basket.total_price = basket.product.all().aggregate(Sum("total_price"))["total_price__sum"]
        basket.total_price = basket.total_price if basket.total_price else 0
        basket.total_price_with_offer = basket.product.all().aggregate(Sum("total_price_with_offer"))[
            "total_price_with_offer__sum"]
        basket.total_price_with_offer = basket.total_price_with_offer if basket.total_price_with_offer else 0
        basket.total_offer_percent = (
                100 - (basket.total_price_with_offer * 100 / basket.total_price)) if basket.total_price else 0

    basket.save()


@receiver(post_save, sender=BasketDetail)
def basket_products_price_updater(sender, **kwargs):
    basket: Basket = kwargs["instance"].basket_set.first()
    if basket:
        if not basket.is_paid:
            basket.count = basket.product.all().aggregate(Sum("count"))["count__sum"]
            basket.count = basket.count if basket.count else 0
            basket.total_price = basket.product.all().aggregate(Sum("total_price"))["total_price__sum"]
            basket.total_price = basket.total_price if basket.total_price else 0
            basket.total_price_with_offer = basket.product.all().aggregate(Sum("total_price_with_offer"))[
                "total_price_with_offer__sum"]
            basket.total_price_with_offer = basket.total_price_with_offer if basket.total_price_with_offer else 0
            basket.total_offer_percent = (
                    100 - (basket.total_price_with_offer * 100 / basket.total_price)) if basket.total_price else 0

        basket.save()
