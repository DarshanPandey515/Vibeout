import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class Campaign(TenantScopedModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("running", "Running"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        "agents.Agent", on_delete=models.PROTECT, related_name="campaigns"
    )
    caller_number = models.ForeignKey(
        "telephony.PhoneNumber", on_delete=models.PROTECT, related_name="campaigns"
    )
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]