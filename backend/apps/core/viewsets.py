from rest_framework import viewsets

from .permissions import IsOrganizationMember


class TenantScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.request.org)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.org)
