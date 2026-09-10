from django.conf import settings
from qstash import QStash

from .models import PipelineRun


def publish_job(job_type, organization, related_object_id, idempotency_key, payload):
    run, created = PipelineRun.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "organization": organization,
            "job_type": job_type,
            "related_object_id": related_object_id,
        },
    )
    if not created and run.status != "failed":
        return run
    if not created:
        run.status = "queued"
        run.error_message = ""
        run.save(update_fields=["status", "error_message"])

    body = {"idempotency_key": idempotency_key, **payload}
    if settings.QSTASH_INLINE:
        # ponytail: dev runs the whole job chain inside the request; set QSTASH_INLINE=false with a public URL for async
        from .views import execute_run

        try:
            execute_run(run, body)
        except Exception:
            pass
        return run

    url = f"{settings.PUBLIC_BASE_URL}/api/v1/jobs/{job_type}"
    QStash(settings.QSTASH_TOKEN).message.publish_json(url=url, body=body, retries=3)
    return run