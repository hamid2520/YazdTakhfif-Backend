from rest_framework.viewsets import ModelViewSet

from .models import Offer
from .filters import IsSuperUserOrOwner
from .serializers import OfferSerializer


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    lookup_field = "offer_code"
    lookup_url_kwarg = "offer_code"
    filter_backends = [IsSuperUserOrOwner, ]
