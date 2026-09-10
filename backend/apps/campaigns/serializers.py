from rest_framework import serializers

from apps.agents.models import Agent
from apps.telephony.models import PhoneNumber

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
    caller_number = serializers.PrimaryKeyRelatedField(queryset=PhoneNumber.objects.all())

    class Meta:
        model = Campaign
        fields = ["id", "name", "agent", "caller_number", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]