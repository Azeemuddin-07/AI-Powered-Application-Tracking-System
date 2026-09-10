from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel


class Skill(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        ordering = ["name"]


class Job(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        PAUSED = "paused", "Paused"
        CLOSED = "closed", "Closed"

    class WorkplaceType(models.TextChoices):
        REMOTE = "remote", "Remote"
        HYBRID = "hybrid", "Hybrid"
        ON_SITE = "on_site", "On-site"

    company = models.ForeignKey("recruiters.Company", on_delete=models.PROTECT, related_name="jobs")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_jobs")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    preferred_qualifications = models.TextField(blank=True)
    experience_level = models.CharField(max_length=64, db_index=True)
    employment_type = models.CharField(max_length=64, db_index=True)
    workplace_type = models.CharField(max_length=16, choices=WorkplaceType.choices, db_index=True)
    location = models.CharField(max_length=160, blank=True, db_index=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    salary_currency = models.CharField(max_length=3, default="USD")
    application_deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    openings = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["company", "status"]),
            models.Index(fields=["workplace_type", "experience_level"]),
        ]


class JobSkill(TimestampedModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="job_skills")
    is_required = models.BooleanField(default=True)
    minimum_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["job", "skill"], name="unique_job_skill")]

