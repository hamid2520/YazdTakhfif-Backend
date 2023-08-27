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
        if self.action == "list":
            return CouponSerializer
        return CouponCreateSerializer


class LineCouponViewSet(ModelViewSet):
    queryset = LineCoupon.objects.all()
    serializer_class = LineCouponSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(coupon__slug=self.kwargs.get("slug"))
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
