from django.db import models


class TenantScopedManager(models.Manager):
    def for_org(self, organization):
        return self.get_queryset().filter(organization=organization)