from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet

from .models import Business
from .filters import IsOwnerOrSuperUser
from .serializers import BusinessSerializer


class BusinessViewSet(ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUser, ]
