from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .models import Basket, BasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail


class BasketViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]

    @action(detail=True, methods=["GET"])
    def get_basket_count(self, request, slug):
        count = self.get_object().count
        return Response(data={"count": count}, status=status.HTTP_200_OK)


class BasketDetailViewSet(ModelViewSet):
    queryset = BasketDetail.objects.all()
    serializer_class = BasketDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasketDetail, ]

    # todo : add an action that returns a basket's products
