"""
Custom permission classes for role-based access control.
"""
from rest_framework import permissions


class IsClient(permissions.BasePermission):
    """Allow access only to users with client role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.is_client()
        )


class IsStaff(permissions.BasePermission):
    """Allow access only to staff members."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.is_staff()
        )


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.is_admin()
        )


class IsAdminOrStaff(permissions.BasePermission):
    """Allow access to admin or staff members."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in ("admin", "staff")
        )


class IsOwnerOrAdminOrStaff(permissions.BasePermission):
    """
    Allow owner, admin, or staff to access an object.
    For reservations, owner is the guest.
    """

    def has_object_permission(self, request, view, obj):
        # Staff and admins can always view
        if (
            hasattr(request.user, "profile")
            and request.user.profile.role in ("admin", "staff")
        ):
            return True

        # Clients can only see their own reservations
        return obj.guest == request.user


class CanCancelOwnReservation(permissions.BasePermission):
    """
    Allow users to cancel only their own reservations.
    Staff and admins can cancel any reservation.
    """

    def has_object_permission(self, request, view, obj):
        # Admin and staff can cancel any reservation
        if (
            hasattr(request.user, "profile")
            and request.user.profile.role in ("admin", "staff")
        ):
            return True

        # Clients can only cancel their own reservations
        return obj.guest == request.user
