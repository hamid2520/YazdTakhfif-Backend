from django.db.models import Q, Sum
from rest_framework import filters
from src.utils.get_bool import get_boolean
from .models import Business, Category, Coupon


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


class PriceQueryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        price = request.query_params.get("price", None)
        if price:
            price = str(price)
            if price == "-10000":
                return queryset.filter(linecoupon__price__lte=10000)
            elif price == "10000-100000":
                return queryset.filter(linecoupon__price__gte=10000, linecoupon__price__lte=100000)
            elif price == "100000-250000":
                return queryset.filter(linecoupon__price__gte=100000, linecoupon__price__lte=250000)
            elif price == "250000-500000":
                return queryset.filter(linecoupon__price__gte=250000, linecoupon__price__lte=500000)
            elif price == "+500000":
                return queryset.filter(linecoupon__price__gte=500000)
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
        if request.GET.get('category', None):
            queryset = queryset.filter(category__slug=str(request.GET.get('category')))
            return queryset
        return queryset


class IsAvailableFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_available = request.query_params.get("is_available")
        if is_available and queryset.exists():
            if get_boolean(is_available):
                return queryset.filter(linecoupon__count__gt=0)
            else:
                return queryset.filter(linecoupon__count=0)
        return queryset


class HotSellsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("ordering")
        if ordering == "hot_sells":
            return queryset.annotate(hot_sells=Sum("linecoupon__sell_count")).order_by(
                "-hot_sells").distinct()
        return queryset


class CustomOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        return super().filter_queryset(request, queryset, view).distinct()


# class RelatedCouponsFilter(filters.BaseFilterBackend):
#     def filter_queryset(self, request, queryset: Coupon.objects.all(), view):
#         coupon_slug = request.query_params.get("related")
#         if coupon_slug:
#             coupon = Coupon.objects.filter(slug=coupon_slug)
#             if coupon.exists():
#                 coupon = coupon.first()
#                 categories_id = coupon.category.all().values_list("id")
#                 print(categories_id)
#                 return queryset.filter(category__id__in=categories_id).distinct().order_by("?")
#         return queryset
