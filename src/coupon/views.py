from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category, Coupon, LineCoupon
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

    def get_serializer_class(self):
        if self.action == ("list" or "retrieve"):
            return CouponSerializer
        return CouponCreateSerializer


class LineCouponViewSet(ModelViewSet):
    serializer_class = LineCouponSerializer
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Coupon.objects.get(slug=self.kwargs.get("slug")).linecoupon_set.all()

    def get_object(self):
        return LineCoupon.objects.get(slug=self.kwargs.get("slug"))
