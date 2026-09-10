from rest_framework.authentication import TokenAuthentication


class OrganizationTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        request.org = None
        result = super().authenticate(request)
        if result is None:
            return None
        user, _ = result
        organization_id = request.headers.get("X-Organization-Id")
        if organization_id:
            membership = (
                user.memberships.select_related("organization")
                .filter(organization_id=organization_id)
                .first()
            )
            if membership:
                request.org = membership.organization
        return result