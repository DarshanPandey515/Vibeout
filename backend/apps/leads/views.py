import hashlib
import json
from pathlib import Path

from botocore.exceptions import ClientError

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.jobs.publish import publish_job
from apps.storage import client as storage

from .models import Lead, LeadContext, LeadImport
from .serializers import (
    LeadContextEditSerializer,
    LeadContextSerializer,
    LeadDetailSerializer,
    LeadImportSerializer,
    LeadSummarySerializer,
    UploadRequestSerializer,
)


def _content_hash(raw_fields):
    return hashlib.sha1(json.dumps(raw_fields, sort_keys=True).encode()).hexdigest()[:16]


def _latest_context(lead):
    return lead.contexts.order_by("-version").first()


class CampaignLeadsUploadView(APIView):
    def post(self, request, campaign_id):
        serializer = UploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data["size_bytes"] > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationError({"error": "file_too_large"})
        ext = Path(data["filename"]).suffix.lower().lstrip(".") or "csv"
        lead_import = LeadImport.objects.create(
            organization=request.org,
            campaign_id=campaign_id,
            filename=data["filename"],
            content_type=data["content_type"],
            size_bytes=data["size_bytes"],
            object_key=storage.import_object_key(request.org.id, "pending", ext),
        )
        lead_import.object_key = storage.import_object_key(request.org.id, lead_import.id, ext)
        lead_import.save(update_fields=["object_key"])
        try:
            upload_url = storage.presigned_put_url(
                lead_import.object_key, data["content_type"]
            )
        except Exception:
            lead_import.delete()
            raise ValidationError({"error": "storage_unavailable"})
        return Response(
            {"upload_url": upload_url, "lead_import_id": lead_import.id},
            status=status.HTTP_201_CREATED,
        )


class LeadImportConfirmView(APIView):
    def post(self, request, import_id):
        lead_import = LeadImport.objects.for_org(request.org).filter(id=import_id).first()
        if not lead_import:
            raise NotFound()
        try:
            head = storage.head_object(lead_import.object_key)
        except ClientError:
            raise ValidationError({"error": "object_missing"})
        if head["ContentLength"] > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationError({"error": "file_too_large"})
        lead_import.status = "parsing"
        lead_import.save(update_fields=["status"])
        try:
            run = publish_job(
                "parse-import",
                request.org,
                lead_import.id,
                f"parse:{lead_import.id}",
                {"lead_import_id": str(lead_import.id)},
            )
        except Exception:
            lead_import.status = "failed"
            lead_import.error_message = "Failed to enqueue parse job."
            lead_import.save(update_fields=["status", "error_message"])
            return Response(
                {"error": "enqueue_failed"}, status=status.HTTP_502_BAD_GATEWAY
            )
        if run.status == "failed":
            lead_import.status = "failed"
            lead_import.error_message = run.error_message or "Parse job failed."
            lead_import.save(update_fields=["status", "error_message"])
            return Response(
                {"error": "parse_failed"}, status=status.HTTP_502_BAD_GATEWAY
            )
        return Response(
            {"lead_import_id": lead_import.id, "status": "parsing"},
            status=status.HTTP_202_ACCEPTED,
        )


class LeadImportStatusView(APIView):
    def get(self, request, import_id):
        lead_import = LeadImport.objects.for_org(request.org).filter(id=import_id).first()
        if not lead_import:
            raise NotFound()
        return Response(LeadImportSerializer(lead_import).data)


class CampaignLeadsView(APIView):
    def get(self, request, campaign_id):
        leads = Lead.objects.for_org(request.org).filter(campaign_id=campaign_id)
        status_filter = request.query_params.get("status")
        if status_filter:
            leads = leads.filter(status=status_filter)
        return Response(LeadSummarySerializer(leads.order_by("created_at"), many=True).data)


class LeadDetailView(APIView):
    def get(self, request, lead_id):
        lead = Lead.objects.for_org(request.org).filter(id=lead_id).first()
        if not lead:
            raise NotFound()
        return Response(LeadDetailSerializer(lead).data)


class LeadContextRegenerateView(APIView):
    def post(self, request, lead_id):
        lead = Lead.objects.for_org(request.org).filter(id=lead_id).first()
        if not lead:
            raise NotFound()
        run = publish_job(
            "generate-context",
            request.org,
            lead.id,
            f"generate:{lead.id}:{_content_hash(lead.raw_fields)}",
            {"lead_id": str(lead.id)},
        )
        return Response({"pipeline_run_id": run.id}, status=status.HTTP_202_ACCEPTED)


class LeadContextEditView(APIView):
    def patch(self, request, lead_id):
        lead = Lead.objects.for_org(request.org).filter(id=lead_id).first()
        if not lead:
            raise NotFound()
        latest = _latest_context(lead)
        if not latest:
            raise ValidationError({"error": "no_context"})
        serializer = LeadContextEditSerializer(latest, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_version = LeadContext.objects.create(
            organization=request.org,
            lead=lead,
            version=latest.version + 1,
            is_edited_by_human=True,
            **serializer.validated_data,
        )
        return Response(LeadContextSerializer(new_version).data)


class LeadContextApproveView(APIView):
    def post(self, request, lead_id):
        lead = Lead.objects.for_org(request.org).filter(id=lead_id).first()
        if not lead:
            raise NotFound()
        latest = _latest_context(lead)
        if not latest:
            raise ValidationError({"error": "no_context"})
        latest.approved_by = request.user
        latest.approved_at = timezone.now()
        latest.save(update_fields=["approved_by", "approved_at"])
        lead.status = "ready"
        lead.save(update_fields=["status"])
        return Response(LeadDetailSerializer(lead).data)