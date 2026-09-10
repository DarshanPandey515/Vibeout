from django.utils.text import slugify
from rest_framework import serializers

from apps.accounts.models import Membership

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "role", "created_at"]

    def get_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = Membership.objects.filter(
            organization=obj, user=request.user
        ).first()
        return membership.role if membership else None


class OrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        request = self.context["request"]
        base_slug = slugify(validated_data["name"]) or "org"
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        organization = Organization.objects.create(name=validated_data["name"], slug=slug)
        Membership.objects.create(organization=organization, user=request.user, role="owner")
        return organization
