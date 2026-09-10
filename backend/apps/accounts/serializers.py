from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.organizations.models import Organization

from .models import Membership

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    org_name = serializers.CharField(max_length=255)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.create_user(
            username=email, email=email, password=validated_data["password"]
        )
        base_slug = slugify(validated_data["org_name"]) or "org"
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        organization = Organization.objects.create(
            name=validated_data["org_name"], slug=slug
        )
        Membership.objects.create(organization=organization, user=user, role="owner")
        token, _ = Token.objects.get_or_create(user=user)
        return {
            "user_id": user.id,
            "organization_id": organization.id,
            "token": token.key,
        }
