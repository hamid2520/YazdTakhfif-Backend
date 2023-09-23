from rest_framework.permissions import BasePermission


class IsSuperUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(user.is_superuser or obj.user_id == user.id)
