from rest_framework import serializers

from .models import Lead, LeadContext, LeadImport


class LeadImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadImport
        fields = [
            "id",
            "campaign",
            "filename",
            "content_type",
            "size_bytes",
            "status",
            "error_message",
            "row_errors",
            "created_at",
        ]
        read_only_fields = fields


class LeadContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadContext
        fields = [
            "id",
            "version",
            "source_facts",
            "extracted_facts",
            "generated_guidance",
            "unknowns",
            "allowed_claims",
            "prohibited_assumptions",
            "opening_guidance",
            "qualification_guidance",
            "agent_notes",
            "is_edited_by_human",
            "approved_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "version",
            "source_facts",
            "extracted_facts",
            "generated_guidance",
            "unknowns",
            "allowed_claims",
            "prohibited_assumptions",
            "opening_guidance",
            "qualification_guidance",
            "agent_notes",
            "is_edited_by_human",
            "approved_at",
            "created_at",
        ]


class LeadSummarySerializer(serializers.ModelSerializer):
    latest_context_version = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "phone_number",
            "company",
            "status",
            "created_at",
            "latest_context_version",
        ]

    def get_latest_context_version(self, obj):
        context = obj.contexts.order_by("-version").first()
        return context.version if context else None


class LeadDetailSerializer(serializers.ModelSerializer):
    latest_context = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "phone_number",
            "company",
            "status",
            "raw_fields",
            "created_at",
            "latest_context",
        ]

    def get_latest_context(self, obj):
        context = obj.contexts.order_by("-version").first()
        return LeadContextSerializer(context).data if context else None


class LeadContextEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadContext
        fields = [
            "source_facts",
            "extracted_facts",
            "generated_guidance",
            "unknowns",
            "allowed_claims",
            "prohibited_assumptions",
            "opening_guidance",
            "qualification_guidance",
            "agent_notes",
        ]


class UploadRequestSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    content_type = serializers.ChoiceField(
        choices=[
            "text/csv",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
    )
    size_bytes = serializers.IntegerField(min_value=1)