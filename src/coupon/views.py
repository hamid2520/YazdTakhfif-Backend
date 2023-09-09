from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.settings import api_settings
from django.core.exceptions import ObjectDoesNotExist

from .models import Category, Coupon, LineCoupon, Rate
from .filters import IsOwnerOrSuperUserCoupon, IsOwnerOrSuperUserLineCoupon
from .serializers import CategorySerializer, CouponSerializer, CouponCreateSerializer, LineCouponSerializer, \
    RateSerializer


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

    @action(detail=True, methods=["GET", "POST"])
    def rate_coupon(self, request, slug):
        coupon = self.get_object()
        try:
            rate_object = Rate.objects.get(user_id=request.user.id, coupon_id=coupon.id)
            serializer = RateSerializer(instance=rate_object, data=request.data)
        except ObjectDoesNotExist:
            serializer = RateSerializer(data=request.data)
        finally:
            if serializer.is_valid():
                serializer.validated_data["user"] = request.user.id
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_200_OK)

        # coupon = self.get_object()
        # rate_object = Rate.objects.filter(user_id=request.user.id, coupon_id=coupon.id)
        # rate_object = rate_object.first()
        # print(rate_object)
        # if rate_object:
        #     print(rate_object)
        #     serializer = RateSerializer(instance=rate_object, data=request.data)
        # else:
        #     serializer = RateSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.validated_data["user"] = request.user.id
        #     serializer.save()
        #     return Response(data=serializer.data, status=status.HTTP_200_OK)
        # return Response(data=serializer.errors, status=status.HTTP_200_OK)


class LineCouponViewSet(ModelViewSet):
    queryset = LineCoupon.objects.all()
    serializer_class = LineCouponSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserLineCoupon, ]

    # todo : action for get a coupon's lines
