import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class Agent(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    objective_template = models.TextField()
    system_prompt_template = models.TextField()
    voice_config = models.JSONField(default=dict)
    guardrails = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name