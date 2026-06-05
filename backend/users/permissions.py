from rest_framework.permissions import BasePermission, SAFE_METHODS


class StaffOrAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        id = view.kwargs.get('id')
        if id is None:
            if request.user and request.user.is_staff:
                return True
            elif request.user.is_authenticated and request.method in SAFE_METHODS:
                return True
            return False
        return True
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            if (obj.is_superuser and obj.id != request.user.id and not request.method in SAFE_METHODS):
                return False
            return True
        if request.user.is_staff:
            if (obj.is_staff and obj.id != request.user.id and not request.method in SAFE_METHODS):
                return False
            return True
        if request.user.is_authenticated:
            if request.method not in SAFE_METHODS and request.user.id != obj.id:
                return False
            return True
        return False
    