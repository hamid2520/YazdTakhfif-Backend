from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from .models import Basket, BasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer


class BasketViewSet(ModelViewSet):
    serializer_class = BasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        queryset = Basket.objects.filter(user__id=self.request.user.id)
        return queryset

    @action(detail=True, methods=["GET"])
    def get_basket_count(self, request, slug):
        count = self.get_object().count
        return Response(data={"count": count}, status=status.HTTP_200_OK)


class BasketDetailViewSet(ModelViewSet):
    serializer_class = BasketDetailSerializer
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Basket.objects.get(slug=self.kwargs.get("slug")).product.all()

    def get_object(self):
        return BasketDetail.objects.get(slug=self.kwargs.get("slug"))
