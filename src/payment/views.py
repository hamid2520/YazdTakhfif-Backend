from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .models import Payment
from .serializers import PaymentSerializer
from src.basket.filters import IsOwnerOrSuperUserBasket


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUserBasket, ]
