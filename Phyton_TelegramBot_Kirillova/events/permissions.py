from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Менять объект может только его владелец."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # у Events поле называется user_id (FK). Приводим к int для сравнения.
        owner_id = getattr(obj, "user_id", None)
        if owner_id is None:
            return False
        return str(owner_id) == str(getattr(request.user, "telegram_id", None))