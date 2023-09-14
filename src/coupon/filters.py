from django.db.models import Q
from rest_framework import filters


class IsOwnerOrSuperUserCoupon(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(business__admin_id=request.user.id)


class IsOwnerOrSuperUserLineCoupon(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(coupon__business__admin_id=request.user.id)


class PriceFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        max_price = request.query_params.get("max_price")
        min_price = request.query_params.get("min_price")
        if max_price and min_price:
            return queryset.filter(Q(linecoupon__price__gte=min_price) & Q(linecoupon__price__lte=max_price))
        elif max_price:
            return queryset.filter(linecoupon__price__lte=max_price)
        elif min_price:
            return queryset.filter(linecoupon__price__gte=min_price)
        return queryset


class RateFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        rate = request.query_params.get("rate")
        if rate:
            return queryset.filter(coupon_rate__gte=rate)
        return queryset


class OfferFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        offer = request.query_params.get("offer")
        if offer:
            return queryset.filter(linecoupon__offer_percent__gte=offer)
        return queryset
