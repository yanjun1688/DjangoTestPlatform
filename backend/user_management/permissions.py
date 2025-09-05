from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    所有认证用户都可以访问，不限制管理员
    """
    def has_permission(self, request, view):
        # 只需要用户已认证即可
        return request.user and request.user.is_authenticated

class IsAdminOrSelf(permissions.BasePermission):
    """
    所有认证用户都可以访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 所有认证用户都可以访问任意用户的信息
        return True 