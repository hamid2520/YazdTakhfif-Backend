from rest_framework import filters


class IsOwnerOrSuperUserCoupon(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(business__admin_id=request.user.id)


class IsOwnerOrSuperUserLineCoupon(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        return queryset.filter(coupon__business__admin_id=request.user.id)
