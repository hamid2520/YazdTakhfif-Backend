from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.settings import api_settings

from .models import Category, Coupon, LineCoupon
from .filters import IsOwnerOrSuperUserCoupon, IsOwnerOrSuperUserLineCoupon
from .serializers import CategorySerializer, CouponSerializer, CouponCreateSerializer, LineCouponSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserCoupon, ]

    def get_serializer_class(self):
        if self.action == ("list" or "retrieve"):
            return CouponSerializer
        return CouponCreateSerializer

    @action(detail=True, methods=["GET"], url_path="line-coupons-list", url_name="line_coupons_list", )
    def get_products_list(self, request, slug):
        line_coupons = self.get_object().linecoupon_set.all()
        serializer = LineCouponSerializer(instance=line_coupons, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class LineCouponViewSet(ModelViewSet):
    queryset = LineCoupon.objects.all()
    serializer_class = LineCouponSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserLineCoupon, ]

    # todo : action for get a coupon's lines
