from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "name", "role", "is_email_verified")

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("name", "email", "password", "confirm_password", "role")

    def validate_role(self, value):
        if value not in (User.Role.CANDIDATE, User.Role.RECRUITER):
            raise serializers.ValidationError("Choose candidate or recruiter.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("name").strip()
        first_name, _, last_name = name.partition(" ")
        user = User(email=validated_data["email"].lower(), username=validated_data["email"].lower(), first_name=first_name, last_name=last_name, role=validated_data["role"])
        user.set_password(validated_data["password"])
        user.save()
        if user.role == User.Role.CANDIDATE:
            from apps.candidates.models import CandidateProfile
            CandidateProfile.objects.create(user=user)
        else:
            from apps.recruiters.models import RecruiterProfile
            RecruiterProfile.objects.create(user=user)
        return user
