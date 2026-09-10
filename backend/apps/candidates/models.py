from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel


class CandidateProfile(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    phone = models.CharField(max_length=32, blank=True)
    location = models.CharField(max_length=160, blank=True, db_index=True)
    photo = models.ImageField(upload_to="profiles/%Y/%m/", blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    professional_summary = models.TextField(blank=True)
    projects = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    profile_completion = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])


class Resume(TimestampedModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/%Y/%m/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    content_hash = models.CharField(max_length=64, db_index=True)
    extracted_text = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=16, default="pending", db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["candidate", "content_hash"], name="unique_candidate_resume_content"),
        ]


class CandidateSkill(TimestampedModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="candidate_skills")
    skill = models.ForeignKey("jobs.Skill", on_delete=models.PROTECT, related_name="candidate_skills")
    proficiency = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    years_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["candidate", "skill"], name="unique_candidate_skill")]


class Education(TimestampedModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=160)
    field_of_study = models.CharField(max_length=160, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)


class Experience(TimestampedModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="experience")
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]


class SavedJob(TimestampedModel):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="saved_by")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["candidate", "job"], name="unique_saved_job")]
