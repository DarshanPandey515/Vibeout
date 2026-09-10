from django.db import models

from apps.core.models import TenantScopedModel


class TwilioAccount(TenantScopedModel):
    twilio_account_sid = models.CharField(max_length=64)
    auth_token_encrypted = models.BinaryField()
    api_key_sid = models.CharField(max_length=64, blank=True)
    api_key_secret_encrypted = models.BinaryField(blank=True, null=True)
    status = models.CharField(max_length=20, default="connected")
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-connected_at"]

        unique_together = [("organization", "twilio_account_sid")]


class PhoneNumber(TenantScopedModel):
    twilio_account = models.ForeignKey(
        TwilioAccount, on_delete=models.CASCADE, related_name="phone_numbers"
    )
    phone_number = models.CharField(max_length=20)
    twilio_sid = models.CharField(max_length=64)
    friendly_name = models.CharField(max_length=255, blank=True)
    voice_webhook_configured = models.BooleanField(default=False)

    class Meta:
        unique_together = [("organization", "phone_number")]
