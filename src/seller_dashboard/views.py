from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
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
        if request.user.is_superuser:
            businesses, created = Business.objects.get_or_create(admin_id=request.user.id, title="یزد تخفیف")
        else:
            businesses = Business.objects.filter(admin_id=request.user.id).first()
            if not businesses.exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SellerDashboardSerializer(instance=businesses,
                                               context={'user_id': request.user.id,
                                                        'superuser': request.user.is_superuser})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SellerDashboardCouponsAPIView(ListAPIView):
    serializer_class = SoldCouponsSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        if self.request.user.is_superuser:
            businesses = Business.objects.all()
        else:
            businesses = Business.objects.filter(admin_id=self.request.user.id)
        sold_coupons = ClosedBasketDetail.objects.filter(line_coupon__coupon__business_id__in=businesses).order_by(
            '-closedbasket__created_at')
        return sold_coupons


class UserCommentList(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.filter(verified=True, parent=None).order_by("created_at")
        else:
            return Comment.objects.filter(verified=True, coupon__business__admin=self.request.user,
                                          parent=None).order_by(
                "-created_at")
