from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import Offer
from ..basket.models import Basket, ClosedBasket
from .filters import IsSuperUserOrOwner
from .serializers import OfferSerializer, OfferValidatorSerializer
from rest_framework import pagination


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    lookup_field = "offer_code"
    lookup_url_kwarg = "offer_code"
    filter_backends = [IsSuperUserOrOwner, ]
    pagination_class = pagination.LimitOffsetPagination

    @action(detail=False, methods=["POST", ], url_path="validate-offer", url_name="validate_offer")
    def validate_offer(self, request):
        serializer = OfferValidatorSerializer(data=self.request.data)
        if serializer.is_valid():
            ser_data = serializer.validated_data
            offer = Offer.objects.get(offer_code=ser_data.get("offer_code"))
            if not offer.start_date < timezone.now() < offer.expire_date:
                data = {
                    "error": "Offer is expired"
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            basket = Basket.objects.get(user_id=self.request.user.id)
            total_basket_price_with_offer = basket.product.all().aggregate(
                total_basket_price_with_offer=Sum("total_price_with_offer"))["total_basket_price_with_offer"]
            products_total_price_with_offer = basket.product.filter(
                line_coupon__coupon__business__in=offer.limited_businesses.all()).aggregate(
                total_offered_products_price=Sum("total_price_with_offer"))["total_offered_products_price"]
            offer_price = ((products_total_price_with_offer * offer.percent) // 100)
            offered_price = total_basket_price_with_offer - (
                offer_price if offer_price < offer.maximum_offer_price else offer.maximum_offer_price)
            data = {
                "offer_percent": offer.percent,
                "offered_price": offered_price,
            }
            if ser_data.get("apply_to_basket", False):
                basket.total_price_with_offer = offered_price
                basket.save()
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
