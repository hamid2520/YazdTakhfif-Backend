from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from django.db.models import F
from src.business.models import Business
from .serializers import SellerDashboardSerializer


class SellerDashboardAPIView(APIView):

    def get(self, request):
        business = get_object_or_404(Business,admin_id=request.user.id)
        serializer = SellerDashboardSerializer(instance=business)
        return Response(serializer.data, status=status.HTTP_200_OK)
