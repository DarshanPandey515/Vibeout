from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.calls.dialing import dial_lead, ensure_voice_webhook
from apps.core.permissions import HasRole
from apps.core.viewsets import TenantScopedViewSet
from apps.telephony.twilio_client import TwilioRestException

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
        try:
            ensure_voice_webhook(campaign)
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
        for lead in ready_leads:
            dial_lead(request.org, campaign, lead, 1)
        campaign.status = "running"
        campaign.save(update_fields=["status"])
        return Response(CampaignSerializer(campaign).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "paused"
        campaign.save(update_fields=["status"])
        return Response(CampaignSerializer(campaign).data)