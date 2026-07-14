from Accounts.models import User
from rest_framework import permissions


class ISListener(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.LISTENER
    
class IsPodcasterOrAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [User.Role.PODCASTER, User.Role.ADMIN]
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'creator'):
            return obj.creator == request.user
        
        elif hasattr(obj, 'podcast'):
            return obj.podcast.creator == request.user
            
        return False