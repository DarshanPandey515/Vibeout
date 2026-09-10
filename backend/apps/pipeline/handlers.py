import hashlib
import json

from django.db.models import Max

from apps.jobs.publish import publish_job
from apps.leads.models import Lead, LeadContext, LeadImport
from apps.storage import client as storage

from .generation import generate_context
from .grounding import validate_context
from .normalization import map_fields, normalize_phone
from .parsing import parse_csv


def _content_hash(raw_fields):
    return hashlib.sha1(
        json.dumps(raw_fields, sort_keys=True).encode()
    ).hexdigest()[:16]


def parse_import(run, payload):
    lead_import = LeadImport.objects.get(id=payload["lead_import_id"])
    content = storage.get_object(lead_import.object_key)
    rows = parse_csv(content)
    row_errors = []
    for index, raw in enumerate(rows, start=2):
        mapped = map_fields(raw)
        phone = normalize_phone(mapped.get("phone"))
        if not phone:
            row_errors.append({"row": index, "error": "invalid_phone"})
            continue
        Lead.objects.update_or_create(
            organization=lead_import.organization,
            lead_import=lead_import,
            phone_number=phone,
            defaults={
                "campaign_id": lead_import.campaign_id,
                "name": mapped.get("name", ""),
                "company": mapped.get("company", ""),
                "raw_fields": raw,
            },
        )
    if row_errors and not Lead.objects.filter(lead_import=lead_import).exists():
        lead_import.status = "failed"
        lead_import.error_message = "No valid leads found in the file."
    else:
        lead_import.status = "parsed"
    lead_import.row_errors = row_errors
    lead_import.save(update_fields=["status", "error_message", "row_errors"])
    if lead_import.status == "parsed":
        for lead in Lead.objects.filter(lead_import=lead_import):
            publish_job(
                "generate-context",
                lead_import.organization,
                lead.id,
                f"generate:{lead.id}:{_content_hash(lead.raw_fields)}",
                {"lead_id": str(lead.id)},
            )


def generate_context_job(run, payload):
    lead = Lead.objects.select_related("campaign", "campaign__agent").get(
        id=payload["lead_id"]
    )
    objective = (
        lead.campaign.agent.objective_template if lead.campaign.agent else ""
    )
    result = generate_context(json.dumps(lead.raw_fields, indent=2), objective)
    kept, _demoted, guidance = validate_context(result)
    version = (
        lead.contexts.aggregate(max_version=Max("version"))["max_version"] or 0
    ) + 1
    LeadContext.objects.create(
        organization=lead.organization,
        lead=lead,
        version=version,
        source_facts=result.source_facts,
        extracted_facts=result.extracted_facts,
        generated_guidance=guidance,
        unknowns=result.unknowns,
        allowed_claims=kept,
        prohibited_assumptions=result.prohibited_assumptions,
        opening_guidance=result.opening_guidance,
        qualification_guidance=result.qualification_guidance,
        agent_notes=result.agent_notes,
    )
    lead.status = "needs_review"
    lead.save(update_fields=["status"])