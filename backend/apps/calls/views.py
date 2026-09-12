from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.viewsets import TenantScopedViewSet
from apps.telephony.twilio_client import TwilioRestException

from .dialing import dial_lead, ensure_voice_webhook
from .models import Call, CallOutcome, CallTranscript
from .serializers import CallDetailSerializer, CallSerializer
from .tokens import verify_call_token


def _bearer_token(request):
    header = request.headers.get("Authorization", "")
    return header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else None


class CallViewSet(TenantScopedViewSet):
    serializer_class = CallSerializer

    def get_queryset(self):
        queryset = Call.objects.for_org(self.request.org).select_related(
            "lead", "outcome"
        )
        campaign = self.request.query_params.get("campaign")
        if campaign:
            queryset = queryset.filter(campaign_id=campaign)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by("-created_at")

    def retrieve(self, request, *args, **kwargs):
        call = self.get_object()
        return Response(CallDetailSerializer(call).data)

    @action(detail=True, methods=["get"])
    def transcript(self, request, pk=None):
        call = self.get_object()
        transcript = getattr(call, "transcript", None)
        turns = transcript.turns if transcript else []
        return Response({"turns": turns})

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        call = self.get_object()
        if call.status not in ("failed", "busy", "no_answer", "canceled"):
            raise ValidationError({"error": "call_not_retryable"})
        try:
            ensure_voice_webhook(call.campaign)
        except TwilioRestException as exc:
            raise ValidationError({"error": "webhook_config_failed", "detail": str(exc)})
        attempt = call.campaign.calls.filter(lead=call.lead).count() + 1
        new_call = dial_lead(request.org, call.campaign, call.lead, attempt)
        if not new_call:
            raise ValidationError({"error": "no_approved_context"})
        return Response(CallSerializer(new_call).data, status=201)


class InternalCallView(APIView):
    permission_classes = [AllowAny]

    def _authorized_call(self, request, call_id):
        token = _bearer_token(request)
        if not token or not verify_call_token(token, call_id):
            return None
        return get_object_or_404(Call, id=call_id)


class TranscriptAppendView(InternalCallView):
    def post(self, request, call_id):
        call = self._authorized_call(request, call_id)
        if not call:
            return Response(status=403)
        transcript, _ = CallTranscript.objects.get_or_create(call=call)
        seq = request.data.get("seq")
        if any(turn.get("seq") == seq for turn in transcript.turns):
            return Response(status=204)
        transcript.turns.append(
            {
                "seq": seq,
                "role": request.data["role"],
                "text": request.data["text"],
                "ts": request.data.get("ts", ""),
                "truncated": request.data.get("truncated", False),
                "state": request.data.get("state", ""),
            }
        )
        transcript.turns.sort(key=lambda turn: turn["seq"])
        transcript.save(update_fields=["turns", "updated_at"])
        return Response(status=204)


class CallStateView(InternalCallView):
    def post(self, request, call_id):
        call = self._authorized_call(request, call_id)
        if not call:
            return Response(status=403)
        new_status = request.data["status"]
        if call.can_transition_to(new_status):
            call.status = new_status
            if request.data.get("started_at"):
                call.started_at = request.data["started_at"]
            if request.data.get("ended_at"):
                call.ended_at = request.data["ended_at"]
            call.save()
        return Response(status=204)


class CallOutcomeView(InternalCallView):
    def post(self, request, call_id):
        call = self._authorized_call(request, call_id)
        if not call:
            return Response(status=403)
        CallOutcome.objects.update_or_create(
            call=call,
            defaults={
                "outcome": request.data["outcome"],
                "notes": request.data.get("notes", ""),
                "metadata": request.data.get("metadata", {}),
            },
        )
        return Response(status=204)