from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrAuthenticatedReadonly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_staff) or
            (request.user.is_authenticated and request.method in SAFE_METHODS)
        )