from django.db import models


class TimestampedModel(models.Model):
    """Base model for records that need an immutable creation time and update time."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
