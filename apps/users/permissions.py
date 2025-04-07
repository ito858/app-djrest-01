from rest_framework import permissions

class IsViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('core.can_view_item')
