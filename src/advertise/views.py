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
    queryset = Advertise.objects.all()
    serializer_class = AdvertiseSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs["param"].lower() == 'true':
            queryset = Advertise.objects.filter(is_slider=True)
            return queryset
        elif self.kwargs["param"].lower() == 'false' : 
            queryset = Advertise.objects.filter(is_slider=False)
            return queryset
        else :
            queryset = Advertise.objects.all()
            return queryset