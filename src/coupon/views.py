from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter

from rest_framework.viewsets import ModelViewSet
from rest_framework.settings import api_settings

from .models import Category, Coupon, LineCoupon, Rate, Comment
from .filters import IsOwnerOrSuperUserCoupon, IsOwnerOrSuperUserLineCoupon, PriceFilter, OfferFilter, RateFilter, \
    BusinessFilter, CategoryFilter
from .serializers import CategorySerializer, CouponSerializer, CouponCreateSerializer, LineCouponSerializer, \
    RateSerializer, CommentSerializer
from .permissions import IsSuperUserOrOwner


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserCoupon, SearchFilter]
    search_fields = ['title', ]


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserCoupon, SearchFilter, PriceFilter,
                                                              OfferFilter, RateFilter, BusinessFilter, CategoryFilter]
    search_fields = ['title', "linecoupon__title"]

    def get_serializer_class(self):
        if self.action == ("list" or "retrieve"):
            return CouponSerializer
        return CouponCreateSerializer

    @swagger_auto_schema(request_body=RateSerializer, responses={200: RateSerializer(), })
    @action(detail=True, methods=["POST", ], serializer_class=RateSerializer, url_path="rate-coupon",
            url_name="rate_coupon")
    def rate_coupon(self, request, slug):
        coupon = self.get_object()
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            rate = Rate.objects.filter(coupon_id=coupon.id, user_id=request.user.id)
            if rate.exists():
                rate = rate.first()
                rate.rate = data.get("rate")
                rate.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            new_rate = Rate.objects.create(coupon_id=coupon.id, user_id=request.user.id, rate=data.get("rate"))
            new_rate.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CommentSerializer, responses={200: CommentSerializer(), })
    @action(detail=True, methods=["POST", ], serializer_class=CommentSerializer, url_path="add-comment",
            url_name="add_comment", )
    def add_comment(self, request, slug):
        serializer = CommentSerializer(data=request.data, context={"request": request, "kwargs": self.kwargs})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE", ], permission_classes=[IsSuperUserOrOwner, ], url_path="delete-comment",
            url_name="delete_comment", lookup_url_kwarg="pk")
    def delete_comment(self, request, slug):
        comment = Comment.objects.filter(id=slug)
        if comment.exists():
            comment = comment.first()
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data={"Error": "Comment not found!"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: LineCouponSerializer(), })
    @action(detail=True, methods=["GET"], url_path="line-coupons-list", url_name="line_coupons_list", )
    def get_line_coupons_list(self, request, slug):
        line_coupons = self.get_object().linecoupon_set.all()
        serializer = LineCouponSerializer(instance=line_coupons, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: CommentSerializer(), })
    @action(detail=True, methods=["GET"], url_path="coupon-comments-list", url_name="coupon_comments_list", )
    def get_coupon_comments_list(self, request, slug):
        coupon = self.get_object()
        coupon_comments = coupon.comment_set.all()
        serializer = CommentSerializer(instance=coupon_comments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class LineCouponViewSet(ModelViewSet):
    queryset = LineCoupon.objects.all()
    serializer_class = LineCouponSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserLineCoupon, SearchFilter, PriceFilter, ]
    search_fields = ['title', "coupon__title"]
