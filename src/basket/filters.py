from rest_framework import filters


class IsOwnerOrSuperUserBasket(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user_id=request.user.id)


class IsOwnerOrSuperUserClosedBasket(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset.filter(status=3)
        return queryset.filter(user_id=request.user.id,status=3)


class IsOwnerOrSuperUserBasketDetail(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(basket__user_id=request.user.id)
