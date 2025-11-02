"""
Custom permissions for authentication
"""
from rest_framework import permissions

from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users
    """
    message = 'Only administrators can perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin()
        )


class IsSupervisorOrAbove(permissions.BasePermission):
    """
    Permission check for supervisor and admin users
    """
    message = 'Only supervisors and administrators can perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_supervisor()
        )


class IsOperatorOrAbove(permissions.BasePermission):
    """
    Permission check for operator, supervisor, and admin users
    """
    message = 'Only operators, supervisors, and administrators can perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_operator()
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission check for resource owner or admin
    """
    message = 'You can only access your own resources unless you are an administrator.'
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_admin():
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Default to checking if object is the user themselves
        return obj == request.user
