from rest_framework import serializers

from .models import Call, CallTranscript


class CallSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    outcome = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = [
            "id",
            "campaign",
            "lead",
            "lead_name",
            "status",
            "twilio_call_sid",
            "started_at",
            "ended_at",
            "created_at",
            "outcome",
        ]

    def get_outcome(self, obj):
        outcome = getattr(obj, "outcome", None)
        return outcome.outcome if outcome else None


class CallDetailSerializer(CallSerializer):
    evaluation = serializers.SerializerMethodField()

    class Meta(CallSerializer.Meta):
        fields = CallSerializer.Meta.fields + ["evaluation"]

    def get_evaluation(self, obj):
        evaluation = getattr(obj, "evaluation", None)
        if not evaluation:
            return None
        return {
            "unsupported_claim_flags": evaluation.unsupported_claim_flags,
            "quality_score": evaluation.quality_score,
            "summary": evaluation.summary,
        }


class CallTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTranscript
        fields = ["turns", "updated_at"]