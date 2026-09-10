from django.utils import timezone
from rest_framework import serializers

from .models import Job, JobSkill, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "slug", "category")


class JobSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(source="skill", queryset=Skill.objects.all(), write_only=True)

    class Meta:
        model = JobSkill
        fields = ("id", "skill", "skill_id", "is_required", "minimum_years")


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    applications_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = ("id", "title", "company", "company_name", "location", "workplace_type", "employment_type", "experience_level", "salary_min", "salary_max", "salary_currency", "status", "published_at", "created_at", "applications_count")


class JobDetailSerializer(JobListSerializer):
    job_skills = JobSkillSerializer(many=True, read_only=True)

    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + ("description", "responsibilities", "requirements", "preferred_qualifications", "application_deadline", "openings", "job_skills")


class JobWriteSerializer(serializers.ModelSerializer):
    skills = JobSkillSerializer(many=True, required=False, write_only=True)
    skill_names = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)

    class Meta:
        model = Job
        fields = ("id", "company", "title", "description", "responsibilities", "requirements", "preferred_qualifications", "experience_level", "employment_type", "workplace_type", "location", "salary_min", "salary_max", "salary_currency", "application_deadline", "openings", "status", "skills", "skill_names")

    def validate(self, attrs):
        if attrs.get("salary_min") and attrs.get("salary_max") and attrs["salary_min"] > attrs["salary_max"]:
            raise serializers.ValidationError({"salary_max": "Maximum salary must be greater than minimum salary."})
        return attrs

    def create(self, validated_data):
        skills = validated_data.pop("skills", [])
        skill_names = validated_data.pop("skill_names", [])
        if validated_data.get("status") == Job.Status.PUBLISHED:
            validated_data["published_at"] = timezone.now()
        job = Job.objects.create(created_by=self.context["request"].user, **validated_data)
        self._replace_skills(job, skills, skill_names)
        return job

    def update(self, instance, validated_data):
        skills = validated_data.pop("skills", None)
        skill_names = validated_data.pop("skill_names", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if instance.status == Job.Status.PUBLISHED and not instance.published_at:
            instance.published_at = timezone.now()
        instance.save()
        if skills is not None or skill_names is not None:
            instance.job_skills.all().delete()
            self._replace_skills(instance, skills or [], skill_names or [])
        return instance

    @staticmethod
    def _replace_skills(job, skills, skill_names=()):
        rows = [JobSkill(job=job, **skill) for skill in skills]
        for name in skill_names:
            cleaned = name.strip()
            if cleaned:
                skill, _ = Skill.objects.get_or_create(name__iexact=cleaned, defaults={"name": cleaned, "slug": cleaned.lower().replace(" ", "-")[:120]})
                if not any(row.skill_id == skill.id for row in rows):
                    rows.append(JobSkill(job=job, skill=skill))
        JobSkill.objects.bulk_create(rows)
