from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import F
from src.business.models import Business
from src.coupon.models import Comment
from .serializers import CommentSerializer
from .serializers import SellerDashboardSerializer, SoldCouponsSerializer
from ..basket.models import ClosedBasketDetail


class SellerDashboardAPIView(APIView):

    def get(self, request):
        business = get_object_or_404(Business, admin_id=request.user.id)
        serializer = SellerDashboardSerializer(instance=business)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class SellerDashboardCouponsAPIView(APIView):
#
#     def get(self, request):
#         business = get_object_or_404(Business, admin_id=request.user.id)
#         sold_coupons = ClosedBasketDetail.objects.filter(line_coupon__coupon__business_id=business.id).order_by(
#             'closedbasket__payment_datetime')
#         serializer = SoldCouponsSerializer(instance=sold_coupons, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class SellerDashboardCouponsAPIView(ListAPIView):
    serializer_class = SoldCouponsSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsAuthenticated, ]

    def get_queryset(self):
        user_id = self.request.user.id
        business = get_object_or_404(Business, admin_id=user_id)
        sold_coupons = ClosedBasketDetail.objects.filter(line_coupon__coupon__business_id=business.id).order_by(
            'closedbasket__payment_datetime')
        return sold_coupons


class UserCommentList(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.filter(verified=True).order_by("created_at")
        else:
            return Comment.objects.filter(verified=True, coupon__business__admin=self.request.user).order_by(
                "created_at")
