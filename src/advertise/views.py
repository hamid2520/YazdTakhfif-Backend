from rest_framework.viewsets import ModelViewSet

from .models import Advertise
from .serializers import AdvertiseSerializer
from .permissions import IsSuperUserOrReadOnly


class AdvertiseViewSet(ModelViewSet):
    queryset = Advertise.objects.all()
    serializer_class = AdvertiseSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]
