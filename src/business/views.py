from rest_framework.generics import CreateAPIView
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Business, DepositRequest, CorporateRequest
from .filters import IsOwnerOrSuperUser
from .serializers import BusinessSerializer, DepositSerializer, CorporateSerializer


class DepositViewSet(ModelViewSet):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DepositRequest.objects.all()
        else:
            return DepositRequest.objects.first(sender=self.request.user)


class CorporateViewSet(CreateAPIView):
    serializer_class = CorporateSerializer
    permission_classes = []
    queryset = CorporateRequest.objects.all()


class BusinessViewSet(ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [IsOwnerOrSuperUser, SearchFilter]
    search_fields = ['title', "admin__username", "admin__first_name", "admin__last_name", ]
    pagination_class = pagination.LimitOffsetPagination
