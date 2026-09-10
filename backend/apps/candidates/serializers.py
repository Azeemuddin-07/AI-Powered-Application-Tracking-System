from rest_framework import serializers

from apps.jobs.models import Skill
from apps.jobs.serializers import SkillSerializer
from .models import CandidateProfile, CandidateSkill, Education, Experience, Resume, SavedJob


class CandidateProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CandidateProfile
        fields = "__all__"
        read_only_fields = ("user", "profile_completion")


class CandidateSkillSerializer(serializers.ModelSerializer):
    skill_detail = SkillSerializer(source="skill", read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(source="skill", queryset=Skill.objects.all(), write_only=True, required=False)
    skill_name = serializers.CharField(write_only=True, required=False, max_length=100)

    class Meta:
        model = CandidateSkill
        fields = ("id", "skill_id", "skill_name", "skill_detail", "proficiency", "years_experience")

    def validate(self, attrs):
        if not attrs.get("skill") and not attrs.get("skill_name"):
            raise serializers.ValidationError("Choose or enter a skill.")
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("skill_name", "").strip()
        if name and "skill" not in validated_data:
            skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name, "slug": name.lower().replace(" ", "-")[:120]})
            validated_data["skill"] = skill
        return super().create(validated_data)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ("candidate",)


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ("candidate",)


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ("id", "file", "original_filename", "file_size", "is_primary", "created_at")
        read_only_fields = ("original_filename", "file_size", "created_at")


class SavedJobSerializer(serializers.ModelSerializer):
    job = serializers.SerializerMethodField()

    class Meta:
        model = SavedJob
        fields = ("id", "job", "created_at")

    def get_job(self, obj):
        from apps.jobs.serializers import JobListSerializer
        return JobListSerializer(obj.job).data
