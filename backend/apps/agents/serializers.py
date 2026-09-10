from rest_framework import serializers

from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "objective_template",
            "system_prompt_template",
            "voice_config",
            "guardrails",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]