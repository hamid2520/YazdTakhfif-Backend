from rest_framework.request import Request
from rest_framework.decorators import APIView
from rest_framework.response import Response
from src.coupon.models import Comment
from .serializers import CommentSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView


# Create your views here.

class UserCommentList(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.filter(verified=True).order_by("created_at")
        else:
            return Comment.objects.filter(verified=True, coupon__business__admin=self.request.user).order_by(
                "created_at")
