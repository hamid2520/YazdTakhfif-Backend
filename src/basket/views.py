from rest_framework.request import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .models import Basket, BasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail
from ..coupon.models import LineCoupon


class BasketViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]

    @action(detail=True, methods=["GET"], url_path="products-list", url_name="products_list", )
    def get_products_list(self, request, slug):
        basket_products = self.get_object().product.all()
        serializer = BasketDetailSerializer(instance=basket_products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="add-to-basket", url_name="add_to_basket", )
    def add_to_basket(self, request, slug):
        line_coupon_slug = request.query_params.get("line_coupon_slug")
        line_coupon_id = LineCoupon.objects.get(slug=line_coupon_slug).id
        basket_product_count = int(request.query_params.get("product_count", 1))
        basket_product = Basket.objects.get(slug=slug).product.filter(line_coupon_id=line_coupon_id)
        if basket_product.exists():
            basket_product = basket_product.first()
            basket_product.count = basket_product_count
            basket_product.save()
            serializer = BasketDetailSerializer(instance=basket_product)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            basket_products = Basket.objects.get(slug=slug)
            basket_product = BasketDetail.objects.create(line_coupon_id=line_coupon_id, count=basket_product_count)
            basket_product.save()
            basket_products.product.add(basket_product)
            basket_products.save()
            serializer = BasketDetailSerializer(instance=basket_product)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"], url_path="delete-from-basket", url_name="delete_from_basket", )
    def delete_from_basket(self, request, slug):
        basket_product = BasketDetail.objects.get(slug=slug)
        basket_product.delete()
        serializer = BasketDetailSerializer(instance=basket_product)
        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

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
