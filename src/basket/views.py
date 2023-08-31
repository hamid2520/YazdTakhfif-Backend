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
        count = self.get_queryset().get(slug=slug).count
        return Response(data={"count": count}, status=status.HTTP_200_OK)


class BasketDetailViewSet(ModelViewSet):
    queryset = BasketDetail.objects.all()
    serializer_class = BasketDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def list(self, request, *args, **kwargs):
        basket = get_object_or_404(Basket, slug=self.kwargs.get("slug"))
        queryset = basket.product.all()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
