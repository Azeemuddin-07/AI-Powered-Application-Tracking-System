from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel


class Application(TimestampedModel):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        UNDER_REVIEW = "under_review", "Under review"
        SHORTLISTED = "shortlisted", "Shortlisted"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    candidate = models.ForeignKey("candidates.CandidateProfile", on_delete=models.PROTECT, related_name="applications")
    job = models.ForeignKey("jobs.Job", on_delete=models.PROTECT, related_name="applications")
    resume = models.ForeignKey("candidates.Resume", on_delete=models.SET_NULL, null=True, related_name="applications")
    cover_letter = models.TextField(blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.APPLIED, db_index=True)
    source = models.CharField(max_length=100, default="platform", db_index=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["candidate", "job"], name="unique_candidate_job_application")]
        indexes = [
            models.Index(fields=["job", "status", "created_at"]),
            models.Index(fields=["candidate", "status"]),
        ]


class ApplicationStatusHistory(TimestampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16, choices=Application.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="application_status_changes")
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]

