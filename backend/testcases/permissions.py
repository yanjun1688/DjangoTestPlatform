from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    所有认证用户可以执行所有操作，不区分管理员和普通用户
    """
    def has_permission(self, request, view):
        # 只需要用户已认证即可
        return request.user and request.user.is_authenticated 