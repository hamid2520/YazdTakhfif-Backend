from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import pagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from src.basket.models import ProductValidationCode
from src.basket.serializers import ProductValidationCodeSerializer, ProductValidationCodeShowSerializer
from .filters import IsOwnerOrSuperUserCoupon, IsOwnerOrSuperUserLineCoupon, PriceFilter, OfferFilter, RateFilter, \
    BusinessFilter, CategoryFilter, SubCategory
from .models import Category, Coupon, LineCoupon, Rate, Comment, CouponImage
from .permissions import IsSuperUserOrOwner, IsSuperUserOrReadOnly
from .serializers import CategorySerializer, CouponSerializer, CouponCreateSerializer, LineCouponSerializer, \
    RateSerializer, CommentSerializer, CouponImageSerializer, LineCouponShowSerializer
from ..utils.get_bool import get_boolean


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsSuperUserOrReadOnly, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [SearchFilter, SubCategory]
    search_fields = ['title', ]
    pagination_class = pagination.LimitOffsetPagination


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserCoupon, SearchFilter, PriceFilter,
                                                              OfferFilter, RateFilter, BusinessFilter, CategoryFilter]
    search_fields = ['title', "linecoupon__title"]
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CouponSerializer
        return CouponCreateSerializer

    @swagger_auto_schema(request_body=CouponImageSerializer, responses={200: CouponImageSerializer(), })
    @action(detail=False, methods=["POST", ], serializer_class=CouponImageSerializer, url_path="add-image",
            url_name="add_image")
    def add_image(self, request):
        serializer = CouponImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE", ], url_path="delete-image", url_name="delete_image")
    def delete_image(self, request, slug):
        coupon = self.get_object()
        image = CouponImage.objects.filter(coupon_id=coupon.id, id=request.data["id"])
        if image.exists():
            image = image.first()
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data={"Error": "No images with this id!"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=RateSerializer, responses={200: RateSerializer(), })
    @action(detail=True, methods=["POST", ], serializer_class=RateSerializer, filter_backends=[],
            url_path="rate-coupon",
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
    @action(detail=True, methods=["POST", ], serializer_class=CommentSerializer, filter_backends=[],
            url_path="add-comment",
            url_name="add_comment", )
    def add_comment(self, request, slug):
        if 'text' in request.data:
            new_comment = Comment.objects.create(user=self.request.user,
                                                 text=str(request.data.get('text', '')),
                                                 coupon=self.get_object(),
                                                 parent_id=request.data.get('parent', None))
            return Response(data=CommentSerializer(instance=new_comment).data, status=status.HTTP_201_CREATED)
        return Response(data={"errors": ['text is required']}, status=status.HTTP_400_BAD_REQUEST)

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
    @action(detail=True, methods=["GET"], url_path="coupon-comments-list", url_name="coupon_comments_list",
            permission_classes=[], filter_backends=[])
    def get_coupon_comments_list(self, request, slug):
        coupon = self.get_object()
        coupon_comments = coupon.comment_set.filter(verified=True)
        serializer = CommentSerializer(instance=coupon_comments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class LineCouponViewSet(ModelViewSet):
    queryset = LineCoupon.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserLineCoupon, SearchFilter, PriceFilter, ]
    search_fields = ['title', "coupon__title"]
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == ("list" or "retrieve"):
            return LineCouponShowSerializer
        return LineCouponSerializer

    @swagger_auto_schema(responses={200: ProductValidationCodeSerializer(), })
    @action(detail=True, methods=["GET"], url_path="line-coupon-code-list", url_name="line_coupon_code_list", )
    def get_line_coupon_codes_list(self, request, slug):
        line_coupon: LineCoupon = self.get_object()
        coupon_codes = line_coupon.productvalidationcode_set.all().order_by("used")
        serializer = ProductValidationCodeSerializer(instance=coupon_codes, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: ProductValidationCodeShowSerializer(), })
    @action(detail=False, methods=["POST"], url_path="line-coupon-code-validation",
            url_name="line_coupon_code_validation", permission_classes=[])
    def line_coupon_codes_validation(self, request):
        code = request.data.get("code")
        code_object = get_object_or_404(ProductValidationCode, code=code)
        if get_boolean(request.data.get('used', False)) and not code_object.used:
            if code_object.product.coupon.business.admin_id == request.user.id or request.user.is_superuser:
                time_now = timezone.now().date()
                expire_date = code_object.product.coupon.expire_date
                if expire_date < time_now:
                    return Response(data={"error": "!کد تخفیف منقضی شده است"}, status=status.HTTP_400_BAD_REQUEST)
                code_object.used = True
                code_object.save()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        data = ProductValidationCodeShowSerializer(instance=code_object).data
        return Response(data=data, status=status.HTTP_200_OK)
