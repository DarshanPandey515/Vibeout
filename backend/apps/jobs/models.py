import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class PipelineRun(TenantScopedModel):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("running", "Running"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.CharField(max_length=50)
    related_object_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    attempt = models.PositiveIntegerField(default=1)
    idempotency_key = models.CharField(max_length=100, unique=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)