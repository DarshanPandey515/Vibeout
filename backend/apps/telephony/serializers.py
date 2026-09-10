from rest_framework import serializers

from .models import PhoneNumber, TwilioAccount


class TwilioAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwilioAccount
        fields = ["id", "twilio_account_sid", "status", "connected_at"]
        read_only_fields = fields


class TwilioAccountCreateSerializer(serializers.Serializer):
    account_sid = serializers.CharField(max_length=64)
    auth_token = serializers.CharField(max_length=128)
    api_key_sid = serializers.CharField(max_length=64, required=False, allow_blank=True)
    api_key_secret = serializers.CharField(
        max_length=128, required=False, allow_blank=True
    )


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "phone_number",
            "twilio_sid",
            "friendly_name",
            "voice_webhook_configured",
        ]
        read_only_fields = fields
