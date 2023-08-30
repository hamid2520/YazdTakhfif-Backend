from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import Basket, BasketDetail
from .serializers import BasketSerializer


class BasketViewSet(ModelViewSet):
    serializer_class = BasketSerializer

    def get_queryset(self):
        queryset = Basket.objects.filter(user__id=self.request.user.id)
        return queryset

    @action(detail=True, methods=["GET"])
    def get_basket_count(self, request, pk):
        count = self.get_queryset().get(pk=pk).count
        return Response(data={"count": count}, status=status.HTTP_200_OK)
