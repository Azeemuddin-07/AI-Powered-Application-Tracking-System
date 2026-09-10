from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimestampedModel


class User(AbstractUser, TimestampedModel):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        RECRUITER = "recruiter", "Recruiter"
        ADMIN = "admin", "Administrator"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, db_index=True)
    is_email_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False, db_index=True)

    REQUIRED_FIELDS = ["email", "role"]


class AuditLog(TimestampedModel):
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=128, db_index=True)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["target_type", "target_id"])]
