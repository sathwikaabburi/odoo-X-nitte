"""
DRF permission classes for role-based access control.

Roles: EMPLOYEE, HR, ADMIN (stored in hr.User.role).
"""
from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    """Allow only users with role EMPLOYEE."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'EMPLOYEE')


class IsHR(BasePermission):
    """Allow only users with role HR."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'HR')


class IsAdmin(BasePermission):
    """Allow only users with role ADMIN."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'ADMIN')


class IsHROrAdmin(BasePermission):
    """Allow HR or ADMIN."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ('HR', 'ADMIN'))


class IsAuthenticated(BasePermission):
    """Any authenticated Dayflow user (hr.User in session)."""

    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'pk') and request.user.pk)


class IsOwnerOrHRAdmin(BasePermission):
    """
    Object-level: allow the owner (matched by employee profile) OR HR/Admin.

    Views that use this must implement `get_owner_profile(obj)` or
    the object itself must have an `employee` FK / `user` FK.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('HR', 'ADMIN'):
            return True
        # Determine ownership — works for attendance, leave, payroll, documents
        if hasattr(obj, 'employee') and hasattr(obj.employee, 'user_id'):
            return obj.employee.user_id == request.user.pk
        # For EmployeeProfile itself
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.pk
        return False
