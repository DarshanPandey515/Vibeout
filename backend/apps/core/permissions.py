from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    message = "An active organization is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.org)


class HasRole(BasePermission):
    def __init__(self, *roles):
        self.roles = roles

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.org):
            return False
        return request.user.memberships.filter(
            organization=request.org, role__in=self.roles
        ).exists()
