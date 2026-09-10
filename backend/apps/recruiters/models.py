from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel


class RecruiterProfile(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recruiter_profile")
    title = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=32, blank=True)


class Company(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    headquarters = models.CharField(max_length=160, blank=True)
    logo = models.ImageField(upload_to="companies/%Y/%m/", blank=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    recruiters = models.ManyToManyField(RecruiterProfile, related_name="companies")
