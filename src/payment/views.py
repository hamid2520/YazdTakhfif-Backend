from rest_framework import pagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.basket.filters import IsOwnerOrSuperUserBasket
from .models import Payment
from .serializers import PaymentSerializer, GiftSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]
    pagination_class = pagination.LimitOffsetPagination


class ValidateGiftAPIView(APIView):
    def get(self, request):
        gift_serializer = GiftSerializer(data=request.data)
        if gift_serializer.is_valid():
            phone = gift_serializer.validated_data.get("phone")
            basket_user = request.user
            if basket_user == phone:
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_200_OK)
        return Response(data=gift_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
