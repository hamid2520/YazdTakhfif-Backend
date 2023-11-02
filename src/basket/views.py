from rest_framework import status
from django.http import HttpResponseNotFound
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from src.utils.custom_api_views import ListRetrieveAPIView
from rest_framework.decorators import APIView
from src.coupon.models import LineCoupon
from .models import Basket, BasketDetail, ClosedBasket
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer, AddToBasketSerializer, ClosedBasketSerializer


class BasketViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]

    @swagger_auto_schema(responses={200: BasketDetailSerializer(many=True), })
    @action(detail=True, methods=["GET"], url_path="products-list", url_name="products_list", )
    def get_products_list(self, request, slug):
        basket_products = self.get_object().product.all()
        serializer = BasketDetailSerializer(instance=basket_products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AddToBasketSerializer, responses={200: AddToBasketSerializer(), })
    @action(detail=True, methods=["POST", ], url_path="add-to-basket", url_name="add_to_basket",
            serializer_class=AddToBasketSerializer)
    def add_to_basket(self, request, slug):
        basket = Basket.objects.filter(slug=slug)
        if basket.exists():
            basket = basket.first()
            add_serializer = AddToBasketSerializer(data=request.data)
            if add_serializer.is_valid():
                data = add_serializer.validated_data
                line_coupon = LineCoupon.objects.get(slug=data.get("line_coupon_slug"))
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
            return Response(data=add_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponseNotFound("Basket not found!")


@action(detail=True, methods=["DELETE"], url_path="delete-from-basket", url_name="delete_from_basket", )
def delete_from_basket(self, request, slug):
    basket_product = BasketDetail.objects.get(slug=slug)
    basket_product.delete()
    return Response(data={}, status=status.HTTP_204_NO_CONTENT)


@action(detail=True, methods=["GET"], url_path="get-basket-count", url_name="get_basket_count", )
def get_basket_count(self, request, slug):
    count = self.get_object().count
    return Response(data={"count": count}, status=status.HTTP_200_OK)


class BasketDetailViewSet(ModelViewSet):
    queryset = BasketDetail.objects.all()
    serializer_class = BasketDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasketDetail, ]


class ClosedBasketAPIView(ListRetrieveAPIView):
    queryset = ClosedBasket.objects.all()
    serializer_class = ClosedBasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, SearchFilter]
    search_fields = ["product__line_coupon__title", ]

    def get(self, request, *args, **kwargs):
        if self.kwargs.get("slug"):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class UserBasketProductCount(APIView):
    def get(self, request):
        try:
            current_user = self.request.user.id
            product_count = Basket.objects.filter(user=current_user).first().product.all()
            return Response(data={'product_count' : len(product_count)}, status=status.HTTP_200_OK)
        except :
            return Response(data={'product_count' : 0}, status=status.HTTP_404_NOT_FOUND)