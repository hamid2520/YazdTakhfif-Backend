from rest_framework.request import Request
from rest_framework.decorators import APIView
from rest_framework.response import Response
from src.coupon.models import Comment
from .serializers import CommentSerializer
from rest_framework import status


# Create your views here.

class UserCommentList(APIView):
    def get(self, request: Request):
        comment = Comment.objects.filter(verified=True, coupon__business__admin=self.request.user)
        comment = CommentSerializer(instance=comment, many=True)
        return Response(data=comment.data, status=status.HTTP_200_OK)
