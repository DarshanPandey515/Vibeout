from django.db import models

from .managers import TenantScopedManager


class TenantScopedModel(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)ss",
    )
    objects = TenantScopedManager()

    class Meta:
        abstract = True
