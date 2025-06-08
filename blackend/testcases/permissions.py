from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    仅管理员可写，其他用户只读
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff 