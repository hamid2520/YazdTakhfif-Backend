from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save, pre_delete
from .models import Basket, BasketDetail, ClosedBasket
from ..wallet.models import Transaction


@receiver(post_save, sender=ClosedBasket)
def make_transaction_for_each_product(sender, **kwargs):
    closed_basket: ClosedBasket = kwargs['instance']
    if not Transaction.objects.filter(closed_basket=closed_basket).exists():
        if closed_basket.status == 2:
            for product in closed_basket.product.all():
                transaction = Transaction(user=product.line_coupon.coupon.business.admin,
                                          amount=product.total_price_with_offer,
                                          price_with_out_offer=product.total_price,
                                          customer=closed_basket.user.username,
                                          coupon_id=product.line_coupon.coupon_id,
                                          line_coupon_id=product.line_coupon_id,
                                          type=1,
                                          status=1)
                transaction.save()


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
    if basket:
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


@receiver(pre_delete, sender=Basket)
def basket_products_remover(sender, **kwargs):
    basket: Basket = kwargs["instance"]
    basket.product.all().delete()
