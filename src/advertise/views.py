from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import pagination
from .models import Advertise
from .serializers import AdvertiseSerializer
from .permissions import IsSuperUserOrReadOnly


class AdvertiseViewSet(ModelViewSet):
    queryset = Advertise.objects.all()
    serializer_class = AdvertiseSerializer
    permission_classes = [IsSuperUserOrReadOnly, ]
    pagination_class = pagination.LimitOffsetPagination


class AdvertiseSliderApiView(generics.ListAPIView):
    queryset = Advertise.objects.all()
    serializer_class = AdvertiseSerializer
    pagination_class = pagination.LimitOffsetPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        is_slider = self.request.GET.get('is_slider', True)
        queryset = Advertise.objects.filter(is_slider=is_slider)
        return queryset