from django.core.files.base import ContentFile
from django.db.models import Q, Sum,F
from rest_framework.permissions import IsAuthenticated
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
from rest_framework import pagination
from .permissions import IsSuperUser
from src.coupon.models import LineCoupon
from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode
from .filters import IsOwnerOrSuperUserBasket, IsOwnerOrSuperUserBasketDetail
from .serializers import BasketSerializer, BasketDetailSerializer, AddToBasketSerializer, ClosedBasketSerializer, \
    ClosedBasketDetailSerializer, ClosedBasketDetailValidatorSerializer, QRCodeSerializer, QRCodeGetSerializer


class BasketViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]
    pagination_class = pagination.LimitOffsetPagination

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
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasketDetail, ]
    pagination_class = pagination.LimitOffsetPagination


class ClosedBasketAPIView(ListRetrieveAPIView):
    queryset = ClosedBasket.objects.all()
    serializer_class = ClosedBasketSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, SearchFilter]
    search_fields = ["product__line_coupon__title", ]
    pagination_class = pagination.LimitOffsetPagination

    def get(self, request, *args, **kwargs):
        if self.kwargs.get("slug"):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class PaidClosedBasketListAPIView(ListAPIView):
    queryset = ClosedBasket.objects.filter(status=2)
    serializer_class = ClosedBasketSerializer
    permission_classes = [IsSuperUser, ]
    pagination_class = pagination.LimitOffsetPagination


class PaidClosedBasketDetailListAPIView(ListAPIView):
    queryset = ClosedBasketDetail.objects.filter(status=1)
    serializer_class = ClosedBasketDetailSerializer
    permission_classes = [IsSuperUser, ]
    pagination_class = pagination.LimitOffsetPagination


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
                            product_codes = ProductValidationCode.objects.filter(product_id=product.line_coupon.id,
                                                                                 used=False,
                                                                                 closed_basket=None).order_by(
                                "id").values("id")
                            if product.count > product_codes.count():
                                product.status = 3
                                product.save()
                                basket.status = 4
                                basket.save()
                                return Response(data={"Error": "There is no more coupon codes for this product!"},
                                                status=status.HTTP_400_BAD_REQUEST)
                            product_codes = product_codes[:product.count]
                            ProductValidationCode.objects.bulk_update(
                                (ProductValidationCode(id=item["id"], closed_basket_id=basket.id) for item in
                                 product_codes),
                                fields=["closed_basket_id", ])
                basket.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


class GetQRCode(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, slug):
        product = ClosedBasketDetail.objects.filter(slug=slug, status=2)
        if product.exists():
            product = product.first()
            closed_basket = product.closedbasket_set.first()
            coupon_codes = product.line_coupon.productvalidationcode_set.filter(closed_basket_id=closed_basket.id)
            codes_list = [
                {"code": text_to_qrcode(
                    request.build_absolute_uri(reverse("verify_qrcode", args=[code.code, ]))),
                    "used": code.used} for code in coupon_codes]
            serializer = QRCodeSerializer(instance=codes_list, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class VerifyQRCode(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, slug):
        code = ProductValidationCode.objects.filter(code=slug)
        if code.exists():
            code = code.first()
            if not code.used:
                serializer = QRCodeGetSerializer(instance=code)
                code.used = True
                code.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data={"Error": "This code has been used"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserBasketProductCount(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        current_user = self.request.user.id
        user_basket = Basket.objects.filter(user=current_user).first()
        if user_basket:
            product_count = user_basket.product.all().count()
            return Response(data={'product_count': product_count}, status=status.HTTP_200_OK)
        else:
            return Response(data={'product_count': 0}, status=status.HTTP_200_OK)


class CurrentUserBasketDetail(APIView):
    def get(self, request):
        basket_detail = ClosedBasketDetail.objects.filter(closedbasket__user=self.request.user.id).annotate(
            linecoupon_title=F('line_coupon__title'), coupon_title=F('line_coupon__coupon__title'), 
            address=F('line_coupon__coupon__business__address'), phonenumber=F('line_coupon__coupon__business__phone_number'),
            )
        serializer = ClosedBasketDetailSerializer(instance=basket_detail, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """
                product__title=F('coupon__title'),
    """