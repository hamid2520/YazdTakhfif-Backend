from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Basket, BasketDetail
from .serializers import BasketSerializer, BasketCreateUpdateSerializer


class BasketViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = Basket.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == ("list" or "retrieve"):
            return BasketSerializer
        return BasketCreateUpdateSerializer

    @action(detail=False, methods=["GET"])
    def get_basket_count(self, request):
        pass
