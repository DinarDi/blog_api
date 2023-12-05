from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaffOrReadOnly(BasePermission):
    """
    The request is authenticated as an owner or staff, or is a read-only request.
    """
    def has_object_permission(self, request, view, obj):
        if obj.status == 'DF':
            # Only the author or staff can get it if the status is draft
            return bool(
                request.user and request.user.is_authenticated and
                (obj.author == request.user or request.user.is_staff)
            )
        else:
            # All users can get it to read
            # but only the author or staff can update
            return bool(
                request.method in SAFE_METHODS or
                request.user and
                request.user.is_authenticated and
                (obj.author == request.user or request.user.is_staff)
            )


class PermissionForUpdate(BasePermission):
    """
    Can update is the status is draft
    """
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in ['PUT', 'PATCH'] and
            (request.data.get('status', None) == 'DF' or
             obj.status == 'DF')
        )
