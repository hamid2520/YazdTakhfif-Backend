from rest_framework.filters import BaseFilterBackend

from src.offer.models import Offer


class IsSuperUserOrOwner(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_superuser:
            return queryset.filter(limited_businesses__admin__id=user.id)
        return queryset
