from rest_framework import filters


class IsOwnerOrSuperUserBasket(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user_id=request.user.id)


class IsOwnerOrSuperUserBasketDetail(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(basket__user_id=request.user.id)
