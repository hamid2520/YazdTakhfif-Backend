from rest_framework.permissions import BasePermission


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method == "GET":
            return user.is_authenticated
        return user.is_superuser


class IsSuperUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(user.is_superuser or obj.user_id == user.id or obj.coupon.business.admin_id == user.id)
