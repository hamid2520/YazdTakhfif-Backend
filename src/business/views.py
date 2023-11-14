from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Business
from .filters import IsOwnerOrSuperUser
from .serializers import BusinessSerializer


class BusinessViewSet(ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUser, SearchFilter]
    search_fields = ['title', "admin__username", "admin__first_name", "admin__last_name", ]
    pagination_class = pagination.LimitOffsetPagination
