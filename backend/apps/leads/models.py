import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class LeadImport(TenantScopedModel):
    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("parsing", "Parsing"),
        ("parsed", "Parsed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="imports",
    )
    object_key = models.CharField(max_length=500)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="uploaded")
    error_message = models.TextField(blank=True)
    row_errors = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class Lead(TenantScopedModel):
    STATUS_CHOICES = [
        ("imported", "Imported"),
        ("processing", "Processing"),
        ("needs_review", "NeedsReview"),
        ("ready", "Ready"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.CASCADE, related_name="leads"
    )
    lead_import = models.ForeignKey(
        LeadImport, on_delete=models.SET_NULL, null=True, related_name="leads"
    )
    name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20)
    company = models.CharField(max_length=255, blank=True)
    raw_fields = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="imported")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("organization", "lead_import", "phone_number")]


class LeadDocument(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="documents")
    object_key = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100)


class LeadContext(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contexts")
    version = models.PositiveIntegerField()
    source_facts = models.JSONField(default=list)
    extracted_facts = models.JSONField(default=list)
    generated_guidance = models.JSONField(default=dict)
    unknowns = models.JSONField(default=list)
    allowed_claims = models.JSONField(default=list)
    prohibited_assumptions = models.JSONField(default=list)
    opening_guidance = models.TextField(blank=True)
    qualification_guidance = models.TextField(blank=True)
    agent_notes = models.TextField(blank=True)
    is_edited_by_human = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("lead", "version")]