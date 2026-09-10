import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class Call(TenantScopedModel):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("dialing", "Dialing"),
        ("in_progress", "InProgress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("no_answer", "NoAnswer"),
        ("busy", "Busy"),
        ("canceled", "Canceled"),
    ]

    STATUS_RANK = {
        "queued": 0,
        "dialing": 1,
        "in_progress": 2,
        "completed": 3,
        "failed": 3,
        "no_answer": 3,
        "busy": 3,
        "canceled": 3,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.CASCADE, related_name="calls"
    )
    lead = models.ForeignKey("leads.Lead", on_delete=models.CASCADE, related_name="calls")
    lead_context = models.ForeignKey(
        "leads.LeadContext", on_delete=models.PROTECT, related_name="calls"
    )
    caller_number = models.ForeignKey(
        "telephony.PhoneNumber", on_delete=models.PROTECT, related_name="calls"
    )
    twilio_call_sid = models.CharField(max_length=64, blank=True)
    livekit_room_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    idempotency_key = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def can_transition_to(self, new_status):
        return Call.STATUS_RANK[new_status] >= Call.STATUS_RANK[self.status]


class CallTranscript(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="transcript")
    turns = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)


class CallOutcome(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="outcome")
    outcome = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)


class CallEvaluation(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.OneToOneField(Call, on_delete=models.CASCADE, related_name="evaluation")
    unsupported_claim_flags = models.JSONField(default=list)
    quality_score = models.FloatField(null=True, blank=True)
    summary = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)