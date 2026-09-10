from django.conf import settings
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.calls.models import Call
from apps.core.permissions import HasRole
from apps.core.viewsets import TenantScopedViewSet
from apps.telephony.twilio_client import (
    TwilioRestException,
    configure_voice_webhook,
    place_call,
)

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignViewSet(TenantScopedViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def get_permissions(self):
        if self.action in ("start", "pause"):
            return [HasRole("owner", "admin")]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status == "running":
            return Response(CampaignSerializer(campaign).data)
        ready_leads = campaign.leads.filter(status="ready")
        if not ready_leads.exists():
            raise ValidationError({"error": "no_call_ready_leads"})
        account = campaign.caller_number.twilio_account
        voice_url = (
            f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/twilio/voice/"
            f"{campaign.caller_number.id}"
        )
        if not campaign.caller_number.voice_webhook_configured:
            try:
                configure_voice_webhook(
                    account, campaign.caller_number.twilio_sid, voice_url
                )
            except TwilioRestException as exc:
                raise ValidationError(
                    {
                        "error": "webhook_config_failed",
                        "detail": (
                            "Twilio requires a public HTTPS webhook URL. "
                            f"Set PUBLIC_BASE_URL to a public URL (e.g. a cloudflared/ngrok tunnel). {exc}"
                        ),
                    }
                )
            campaign.caller_number.voice_webhook_configured = True
            campaign.caller_number.save(update_fields=["voice_webhook_configured"])
        for lead in ready_leads:
            context = (
                lead.contexts.filter(approved_at__isnull=False)
                .order_by("-version")
                .first()
            )
            if not context:
                continue
            call = Call.objects.create(
                organization=request.org,
                campaign=campaign,
                lead=lead,
                lead_context=context,
                caller_number=campaign.caller_number,
                idempotency_key=f"call:{lead.id}:{campaign.id}:1",
            )
            status_callback = (
                f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/twilio/status/{call.id}"
            )
            try:
                twilio_call = place_call(
                    account,
                    lead.phone_number,
                    campaign.caller_number.phone_number,
                    voice_url,
                    status_callback,
                )
                call.twilio_call_sid = twilio_call.sid
                call.status = "dialing"
            except Exception:
                call.status = "failed"
            call.save()
        campaign.status = "running"
        campaign.save(update_fields=["status"])
        return Response(CampaignSerializer(campaign).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "paused"
        campaign.save(update_fields=["status"])
        return Response(CampaignSerializer(campaign).data)