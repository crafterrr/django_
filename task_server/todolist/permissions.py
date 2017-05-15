from rest_framework import permissions
from .models import Tasklist


class IsOwnerOrDeny(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # if request.method in permissions.SAFE_METHODS:
        #     return True.
        if isinstance(obj, Tasklist):
            return obj.owner == request.user
        else:
            return obj.tasklist.owner == request.user
