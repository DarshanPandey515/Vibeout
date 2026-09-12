from django.conf import settings

from apps.telephony.twilio_client import configure_voice_webhook, place_call

from .models import Call


def voice_url_for(campaign):
    return f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/twilio/voice/{campaign.caller_number.id}"


def ensure_voice_webhook(campaign):
    if not campaign.caller_number.voice_webhook_configured:
        configure_voice_webhook(
            campaign.caller_number.twilio_account,
            campaign.caller_number.twilio_sid,
            voice_url_for(campaign),
        )
        campaign.caller_number.voice_webhook_configured = True
        campaign.caller_number.save(update_fields=["voice_webhook_configured"])


def dial_lead(organization, campaign, lead, attempt):
    context = (
        lead.contexts.filter(approved_at__isnull=False).order_by("-version").first()
    )
    if not context:
        return None
    call = Call.objects.create(
        organization=organization,
        campaign=campaign,
        lead=lead,
        lead_context=context,
        caller_number=campaign.caller_number,
        idempotency_key=f"call:{lead.id}:{campaign.id}:{attempt}",
    )
    status_callback = f"{settings.PUBLIC_BASE_URL}/api/v1/webhooks/twilio/status/{call.id}"
    try:
        twilio_call = place_call(
            campaign.caller_number.twilio_account,
            lead.phone_number,
            campaign.caller_number.phone_number,
            voice_url_for(campaign),
            status_callback,
        )
        call.twilio_call_sid = twilio_call.sid
        call.status = "dialing"
    except Exception:
        call.status = "failed"
    call.save()
    return call