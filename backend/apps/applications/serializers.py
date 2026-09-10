from rest_framework import serializers

from apps.candidates.models import Resume
from .models import Application, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ("id", "from_status", "to_status", "reason", "changed_by_name", "created_at")


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True)
    candidate_name = serializers.CharField(source="candidate.user.get_full_name", read_only=True)
    candidate_email = serializers.EmailField(source="candidate.user.email", read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = ("id", "job", "job_title", "company_name", "candidate", "candidate_name", "candidate_email", "resume", "cover_letter", "expected_salary", "status", "source", "created_at", "withdrawn_at", "status_history")
        read_only_fields = ("candidate", "status", "source", "withdrawn_at")

    def validate_resume(self, resume):
        if resume.candidate_id != self.context["request"].user.candidate_profile.id:
            raise serializers.ValidationError("Choose one of your uploaded resumes.")
        return resume


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.Status.choices)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)
