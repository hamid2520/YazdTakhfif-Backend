from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import F
from src.business.models import Business
from src.coupon.models import Comment
from .serializers import CommentSerializer
from .serializers import SellerDashboardSerializer


class SellerDashboardAPIView(APIView):

    def get(self, request):
        business = get_object_or_404(Business,admin_id=request.user.id)
        serializer = SellerDashboardSerializer(instance=business)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCommentList(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.filter(verified=True).order_by("created_at")
        else:
            return Comment.objects.filter(verified=True, coupon__business__admin=self.request.user).order_by(
                "created_at")
