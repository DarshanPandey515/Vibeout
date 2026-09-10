from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.crypto import encrypt
from apps.core.permissions import HasRole
from apps.core.viewsets import TenantScopedViewSet

from .models import PhoneNumber, TwilioAccount
from .serializers import (
    PhoneNumberSerializer,
    TwilioAccountCreateSerializer,
    TwilioAccountSerializer,
)
from .twilio_client import TwilioRestException, list_incoming_numbers, verify_credentials


class TwilioAccountViewSet(TenantScopedViewSet):
    serializer_class = TwilioAccountSerializer

    def get_permissions(self):
        return [HasRole("owner", "admin")]

    def get_queryset(self):
        return TwilioAccount.objects.for_org(self.request.org)

    def create(self, request, *args, **kwargs):
        serializer = TwilioAccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            verify_credentials(data["account_sid"], data["auth_token"])
        except TwilioRestException:
            raise ValidationError({"error": "invalid_credentials"})
        except Exception:
            raise ValidationError(
                {"error": "twilio_unavailable", "detail": "Twilio API is unreachable."}
            )
        api_key_secret_encrypted = (
            encrypt(data["api_key_secret"]) if data.get("api_key_secret") else None
        )
        account, _ = TwilioAccount.objects.update_or_create(
            organization=request.org,
            twilio_account_sid=data["account_sid"],
            defaults={
                "auth_token_encrypted": encrypt(data["auth_token"]),
                "api_key_sid": data.get("api_key_sid", ""),
                "api_key_secret_encrypted": api_key_secret_encrypted,
                "status": "connected",
            },
        )
        return Response(
            TwilioAccountSerializer(account).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="sync-numbers")
    def sync_numbers(self, request, pk=None):
        account = self.get_object()
        try:
            numbers = list_incoming_numbers(account)
        except TwilioRestException:
            raise ValidationError({"error": "invalid_credentials"})
        except Exception:
            raise ValidationError(
                {"error": "twilio_unavailable", "detail": "Twilio API is unreachable."}
            )
        created = []
        with transaction.atomic():
            for number in numbers:
                obj, _ = PhoneNumber.objects.update_or_create(
                    organization=request.org,
                    phone_number=str(number.phone_number),
                    defaults={
                        "twilio_account": account,
                        "twilio_sid": number.sid,
                        "friendly_name": number.friendly_name or "",
                    },
                )
                created.append(obj)
        return Response(PhoneNumberSerializer(created, many=True).data)


class PhoneNumberViewSet(TenantScopedViewSet):
    serializer_class = PhoneNumberSerializer

    def get_queryset(self):
        return PhoneNumber.objects.for_org(self.request.org).order_by("phone_number")