from rest_framework import generics, status, mixins
from django.http import HttpResponseBadRequest
from rest_framework.response import Response

from .models import Business
from .serializers import BusinessSerializer


class BusinessListApiView(generics.ListCreateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class BusinessDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Business.objects.all()
    lookup_field = "slug"
    serializer_class = BusinessSerializer


