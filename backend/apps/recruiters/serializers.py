from rest_framework import serializers

from .models import Company, RecruiterProfile


class RecruiterProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = RecruiterProfile
        fields = ("id", "name", "email", "title", "phone")


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "slug", "website", "description", "headquarters", "logo", "is_verified", "created_at")
        read_only_fields = ("is_verified", "created_at")
