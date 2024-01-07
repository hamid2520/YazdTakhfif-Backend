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
from ..basket.models import Basket
from ..users.models import User


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]
    pagination_class = pagination.LimitOffsetPagination


class ValidateGiftAPIView(APIView):
    def post(self, request):
        gift_serializer = GiftSerializer(data=request.data)
        if gift_serializer.is_valid():
            phone = gift_serializer.validated_data.get("phone")
            email = gift_serializer.validated_data.get("email")
            first_name = gift_serializer.validated_data.get("first_name")
            last_name = gift_serializer.validated_data.get("last_name")
            basket_user = request.user
            basket, created = Basket.objects.get_or_create(user_id=basket_user.id)
            if not (basket_user.phone or basket_user.username) == phone:
                gifted_user, created = User.objects.get_or_create(username=phone)
                gifted_user.save()
                basket.gifted = gifted_user.username
                basket.save()
                basket_user = gifted_user
            basket_user.phone = phone if not basket_user.phone else basket_user.phone
            basket_user.email = email if not basket_user.email else basket_user.email
            basket_user.first_name = first_name if not basket_user.first_name else basket_user.first_name
            basket_user.last_name = last_name if not basket_user.last_name else basket_user.last_name
            basket_user.save()
            return Response(data=gift_serializer.data, status=status.HTTP_200_OK)
        return Response(data=gift_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
