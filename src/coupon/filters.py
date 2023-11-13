from django.db.models import Q
from rest_framework import filters
from utils.get_bool import get_boolean
from .models import Business, Category


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
            return queryset.filter(Q(linecoupon__price__gte=min_price) & Q(linecoupon__price__lte=max_price)).distinct()
        elif max_price:
            return queryset.filter(linecoupon__price__lte=max_price).distinct()
        elif min_price:
            return queryset.filter(linecoupon__price__gte=min_price).distinct()
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
            return queryset.filter(linecoupon__offer_percent__gte=offer).distinct()
        return queryset


class BusinessFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        business_slug = request.query_params.get("business")
        if business_slug:
            business = Business.objects.filter(slug=business_slug)
            if business.exists():
                business = business.first()
                return queryset.filter(business_id=business.id)
            return queryset.filter(business_id=None)
        return queryset


class CategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        category_slug = request.query_params.get("category")
        if category_slug:
            category = Category.objects.filter(slug=category_slug)
            if category.exists():
                category = category.first()
                return queryset.filter(category=category)
            return queryset.filter(category=None)
        return queryset


class IsAvailableFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_available = request.query_params.get("is_available")
        if is_available:
            if get_boolean(is_available):
                return queryset.filter(linecoupon__count__gt=0)
            else:
                return queryset.filter(linecoupon__count=0)
        return queryset
