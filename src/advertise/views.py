from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import pagination
from .models import Advertise, NewsLetter
from .serializers import AdvertiseSerializer, NewsLetterSerializer
from .permissions import IsSuperUserOrReadOnly
from src.utils.get_bool import get_boolean


class NewsLetterViewSet(ModelViewSet):
    queryset = NewsLetter.objects.all()
    serializer_class = NewsLetterSerializer
    permission_classes = []
    pagination_class = pagination.LimitOffsetPagination

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
        is_slider = get_boolean(self.request.GET.get('is_slider', True))
        queryset = Advertise.objects.filter(is_slider=is_slider)
        return queryset