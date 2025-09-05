from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsAdminOrSelf(permissions.BasePermission):
    """
    管理员可以访问所有用户，普通用户只能访问自己的信息
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有用户
        if request.user.is_admin:
            return True
        # 普通用户只能访问自己的信息
        return obj == request.user 