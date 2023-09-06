from rest_framework import filters


class IsOwnerOrSuperUser(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(admin_id=request.user.id)
