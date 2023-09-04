from rest_framework.viewsets import ModelViewSet

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
