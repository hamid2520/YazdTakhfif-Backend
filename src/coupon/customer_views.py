from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
from src.utils.custom_api_views import ListRetrieveAPIView
from .models import Category, Coupon, LineCoupon
from .serializers import CategorySerializer, CouponSerializer, LineCouponSerializer
from .filters import PriceFilter, OfferFilter, RateFilter, BusinessFilter, CategoryFilter


class CategoryAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [SearchFilter]
    search_fields = ['title', ]


class CouponAPIView(ListRetrieveAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [SearchFilter, PriceFilter, OfferFilter, RateFilter,
                                                              BusinessFilter, CategoryFilter]
    search_fields = ['title', "linecoupon__title"]

    def get(self, request, *args, **kwargs):
        if kwargs.get("slug"):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class LineCouponAPIView(ListAPIView):
    serializer_class = LineCouponSerializer
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [SearchFilter, PriceFilter]
    search_fields = ['title', "coupon__title"]

    def get_queryset(self):
        coupon = Coupon.objects.get(slug=self.kwargs.get("coupon_slug"))
        return coupon.linecoupon_set.all()
