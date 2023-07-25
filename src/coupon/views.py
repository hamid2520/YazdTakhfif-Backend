from rest_framework import generics, status, mixins
from django.http import HttpResponseBadRequest
from rest_framework.response import Response

from .models import Category, Coupon, LineCoupon, LineCouponDetail
from .serializers import CategorySerializer, CouponSerializer, LineCouponSerializer, LineCouponDetailSerializer


class CategoryListApiView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = "slug"
    serializer_class = CategorySerializer


class CouponListApiView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer


class CouponDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    lookup_field = "slug"
    serializer_class = CouponSerializer


class LineCouponListApiView(generics.ListCreateAPIView):
    queryset = LineCoupon.objects.all()
    serializer_class = LineCouponSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(coupon__slug=self.kwargs.get("slug"))
        return queryset


