from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save

from .models import Basket, BasketDetail


@receiver(m2m_changed, sender=Basket.product.through)
def basket_products_price_updater(sender, **kwargs):
    basket: Basket = kwargs["instance"]
    if not basket.is_paid:
        details = basket.product.all().aggregate(Sum("count"), Sum("total_price"), Sum("total_price_with_offer"))
        basket_count = details["count__sum"]
        basket_count = basket_count if basket_count else 0
        basket.count = basket_count
        basket.total_price = details["total_price__sum"]
        basket.total_price = basket.total_price if basket.total_price else 0
        basket.total_price_with_offer = details["total_price_with_offer__sum"]
        basket.total_price_with_offer = basket.total_price_with_offer if basket.total_price_with_offer else 0
        basket.total_offer_percent = (
                100 - (basket.total_price_with_offer * 100 / basket.total_price)) if basket.total_price else 0

    basket.save()


@receiver(post_save, sender=BasketDetail)
def basket_products_price_updater(sender, **kwargs):
    basket: Basket = kwargs["instance"].basket_set.first()
    if basket:  # todo
        if not basket.is_paid:
            details = basket.product.all().aggregate(Sum("count"), Sum("total_price"), Sum("total_price_with_offer"))
            basket_count = details["count__sum"]
            basket_count = basket_count if basket_count else 0
            basket.count = basket_count
            basket.total_price = details["total_price__sum"]
            basket.total_price = basket.total_price if basket.total_price else 0
            basket.total_price_with_offer = details["total_price_with_offer__sum"]
            basket.total_price_with_offer = basket.total_price_with_offer if basket.total_price_with_offer else 0
            basket.total_offer_percent = (
                    100 - (basket.total_price_with_offer * 100 / basket.total_price)) if basket.total_price else 0

        basket.save()
