from rest_framework.permissions import BasePermission

from src.basket.models import ClosedBasketDetail


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsOwnerOrSuperUser(BasePermission):
    def has_object_permission(self, request, view, obj: ClosedBasketDetail):
        closed_basket_user_id = obj.closedbasket_set.first().user.id
        return bool(
            request.user.is_superuser or
            request.user.id == closed_basket_user_id
        )
