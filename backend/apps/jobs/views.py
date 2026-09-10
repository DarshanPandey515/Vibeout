import json

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from qstash import Receiver
from qstash.errors import SignatureError

from .models import PipelineRun
from .registry import HANDLERS


def execute_run(run, payload):
    run.status = "running"
    run.started_at = timezone.now()
    run.save(update_fields=["status", "started_at"])
    try:
        HANDLERS[run.job_type](run, payload)
    except Exception as exc:
        run.status = "failed"
        run.error_message = str(exc)
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error_message", "finished_at"])
        raise
    run.status = "succeeded"
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "finished_at"])


class SignedJobView(View):
    def post(self, request, *args, **kwargs):
        body = request.body.decode("utf-8")
        try:
            Receiver(
                settings.QSTASH_CURRENT_SIGNING_KEY,
                settings.QSTASH_NEXT_SIGNING_KEY,
            ).verify(
                signature=request.headers.get("Upstash-Signature", ""),
                body=body,
                url=f"{settings.PUBLIC_BASE_URL}{request.path}",
            )
        except SignatureError:
            return JsonResponse({"error": "invalid_signature"}, status=403)

        payload = json.loads(body)
        run = PipelineRun.objects.filter(
            idempotency_key=payload["idempotency_key"]
        ).first()
        if not run:
            return JsonResponse({"error": "unknown_run"}, status=404)
        if run.status in ("succeeded", "running"):
            return JsonResponse({"status": run.status}, status=200)
        execute_run(run, payload)
        return JsonResponse({"status": "succeeded"})