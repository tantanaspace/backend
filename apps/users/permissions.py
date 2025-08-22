from rest_framework.permissions import BasePermission


class IsSuperAdminUser(BasePermission):
    """
    Allows access only to super admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)
    

class IsDefaultUser(BasePermission):
    """
    Allows access only to default users.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == request.user.Role.USER)
    

class IsHostUser(BasePermission):
    """
    Allows access only to company hosts.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == request.user.Role.HOST)
    

