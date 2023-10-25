from django.core.files.base import ContentFile
from django.db.models import Q, Sum
from src.utils.qrcode_generator import text_to_qrcode
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseNotFound
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from src.utils.custom_api_views import ListRetrieveAPIView

from .permissions import IsSuperUser
from src.coupon.models import LineCoupon
from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer, AddToBasketSerializer, ClosedBasketSerializer, \
    ClosedBasketDetailSerializer, ClosedBasketDetailValidatorSerializer, QRCodeSerializer


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


class PaidClosedBasketListAPIView(ListAPIView):
    queryset = ClosedBasket.objects.filter(status=2)
    serializer_class = ClosedBasketSerializer
    permission_classes = [IsSuperUser, ]


class PaidClosedBasketDetailListAPIView(ListAPIView):
    queryset = ClosedBasketDetail.objects.filter(status=1)
    serializer_class = ClosedBasketDetailSerializer
    permission_classes = [IsSuperUser, ]


class ClosedBasketDetailValidatorAPIView(APIView):
    permission_classes = [IsSuperUser, ]

    def post(self, request, slug):
        basket_product = ClosedBasketDetail.objects.filter(slug=slug)
        if basket_product.exists():
            basket_product = basket_product.first()
            serializer = ClosedBasketDetailValidatorSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                basket_product.status = data.get("status")
                basket_product.save()
                basket = basket_product.closedbasket_set.first()
                not_verified_products = basket.product.filter(status=1)
                if not not_verified_products.exists():
                    canceled_products = basket.product.filter(status=3)
                    if canceled_products.exists():
                        basket.status = 4
                    else:
                        basket.status = 3
                    for product in basket.product.all():
                        for i in range(0, product.count):
                            coupon_code = ProductValidationCode.objects.create(product_id=product.id)
                            coupon_code.save()
                basket.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


class GetQRCode(APIView):
    def get(self, request, slug):
        product = ClosedBasketDetail.objects.filter(slug=slug)
        if product.exists():
            product = product.first()
            coupon_codes = product.productvalidationcode_set.all()
            codes_list = [
                {"code": text_to_qrcode(
                    request.build_absolute_uri(reverse("verify_qrcode", args=[code.code, ]))),
                    "used": code.used} for code in coupon_codes]
            serializer = QRCodeSerializer(instance=codes_list, many=True)
            # print(request.get_host())
            # print(request.build_absolute_uri(reverse("verify_qrcode", args=[slug, ])))
            print(codes_list[-1])
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class VerifyQRCode(APIView):
    def get(self, request, slug):
        code = ProductValidationCode.objects.filter(code=slug)
        if code.exists():
            code = code.first()
            if not code.used:
                serializer = QRCodeSerializer(instance=code)
                code.used = True
                code.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data={"Error": "This code has been used"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
