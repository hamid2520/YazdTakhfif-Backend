from rest_framework.viewsets import ModelViewSet
from rest_framework import generics

from .models import Advertise
from .serializers import AdvertiseSerializer
from .permissions import IsSuperUserOrReadOnly


class AdvertiseViewSet(ModelViewSet):
    queryset = Advertise.objects.all()
    serializer_class = AdvertiseSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]


class AdvertiseSliderApiView(generics.ListAPIView):
    queryset = Advertise.objects.filter(is_slider=True)
    serializer_class = AdvertiseSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]
