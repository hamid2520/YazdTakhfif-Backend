from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .models import Basket, BasketDetail
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer, AddToBasketSerializer
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

    @action(detail=True, methods=["POST", ], url_path="add-to-basket", url_name="add_to_basket",
            serializer_class=AddToBasketSerializer)
    def add_to_basket(self, request, slug):
        add_serializer = AddToBasketSerializer(data=request.data)
        if add_serializer.is_valid():
            data = add_serializer.validated_data
            line_coupon_slug = data.get("line_coupon_slug")
            line_coupon = LineCoupon.objects.filter(slug=line_coupon_slug)
            if line_coupon.exists():
                line_coupon = line_coupon.first()
                basket = Basket.objects.get(slug=slug)
                product = basket.product.filter(line_coupon_id=line_coupon.id)
                product_count = data.get("basket_detail_count")
                if product.exists():
                    product = product.first()
                    product.count = product_count
                    product.save()
                else:
                    product = BasketDetail.objects.create(line_coupon_id=line_coupon.id, count=product_count)
                    product.save()
                    basket.product.add(product)
                    basket.save()
                return Response(data=add_serializer.data, status=status.HTTP_200_OK)
            return Response(data={"line_coupon": ["Not found!", ]}, status=status.HTTP_404_NOT_FOUND)
        return Response(data=add_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
