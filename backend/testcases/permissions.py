from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    仅管理员可写，其他用户只读
    """
    def has_permission(self, request, view):
        # Authenticated users only
        if not (request.user and request.user.is_authenticated):
            return False
        # Read-only for non-admins, write for admins
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff 