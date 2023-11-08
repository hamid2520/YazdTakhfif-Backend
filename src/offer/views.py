from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import Offer
from ..basket.models import Basket, ClosedBasket
from .filters import IsSuperUserOrOwner
from .serializers import OfferSerializer, OfferValidatorSerializer


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    lookup_field = "offer_code"
    lookup_url_kwarg = "offer_code"
    filter_backends = [IsSuperUserOrOwner, ]

    @action(detail=False, methods=["POST", ], url_path="validate-offer", url_name="validate_offer")
    def validate_offer(self, offer_code):
        serializer = OfferValidatorSerializer(data=self.request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            offer = Offer.objects.get(offer_code=data.get("offer_code"))
            basket = Basket.objects.get(slug=data.get("basket_slug"))
            products_total_price = basket.product.filter(
                line_coupon__coupon__business__in=offer.limited_businesses.all()).aggregate(
                total_offered_products_price=Sum("total_price_with_offer"))["total_offered_products_price"]
            offered_price = basket.total_price_with_offer - ((products_total_price * offer.percent) // 100)
            data = {
                "offer_percent": offer.percent,
                "offered_price": offered_price,
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
