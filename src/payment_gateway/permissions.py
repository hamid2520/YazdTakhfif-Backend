from rest_framework.permissions import BasePermission


class IsOwnerOrSuperUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser or
                    obj.user_id == request.user.id)
