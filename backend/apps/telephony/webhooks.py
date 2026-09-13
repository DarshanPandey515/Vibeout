from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse

from apps.calls.models import Call
from apps.core.crypto import decrypt

from .models import PhoneNumber

_TWILIO_STATUS_MAP = {
    "queued": "queued",
    "ringing": "dialing",
    "in-progress": "in_progress",
    "completed": "completed",
    "busy": "busy",
    "failed": "failed",
    "no-answer": "no_answer",
    "canceled": "canceled",
}


def _valid(request, account):
    validator = RequestValidator(decrypt(account.auth_token_encrypted))
    return validator.validate(
        f"{settings.PUBLIC_BASE_URL}{request.path}",
        request.POST,
        request.META.get("HTTP_X_TWILIO_SIGNATURE", ""),
    )


@method_decorator(csrf_exempt, name="dispatch")
class VoiceWebhookView(View):
    def post(self, request, phone_number_id):
        phone_number = (
            PhoneNumber.objects.select_related("twilio_account")
            .filter(id=phone_number_id)
            .first()
        )
        if not phone_number or not _valid(request, phone_number.twilio_account):
            return HttpResponse(status=403)
        response = VoiceResponse()
        call = Call.objects.filter(
            twilio_call_sid=request.POST.get("CallSid", "")
        ).first()
        host = settings.LIVEKIT_SIP_URI.removeprefix("sip:")
        if settings.LIVEKIT_SIP_URI and call and call.livekit_room_name:
            response.dial().sip(f"sip:{call.livekit_room_name}@{host}")
        else:
            response.say("The line is currently unavailable. Goodbye.")
            response.hangup()
        return HttpResponse(str(response), content_type="application/xml")


@method_decorator(csrf_exempt, name="dispatch")
class StatusCallbackView(View):
    def post(self, request, call_id):
        call = (
            Call.objects.select_related("caller_number__twilio_account")
            .filter(id=call_id)
            .first()
        )
        if not call or not _valid(request, call.caller_number.twilio_account):
            return HttpResponse(status=403)
        new_status = _TWILIO_STATUS_MAP.get(request.POST.get("CallStatus", ""))
        if new_status and call.can_transition_to(new_status):
            call.status = new_status
            if new_status == "in_progress":
                call.started_at = timezone.now()
            if new_status in ("completed", "failed", "busy", "no_answer", "canceled"):
                call.ended_at = timezone.now()
            call.save(update_fields=["status", "started_at", "ended_at"])
        return HttpResponse(status=204)