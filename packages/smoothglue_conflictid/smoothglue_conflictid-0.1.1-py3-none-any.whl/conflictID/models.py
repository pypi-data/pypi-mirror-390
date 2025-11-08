from django.contrib.postgres.fields import (
    DateTimeRangeField,
    IntegerRangeField,
)
from django.contrib.postgres.indexes import GistIndex
from django.db import models


class ConflictItem(models.Model):
    """
    A generic, indexed "shadow" record for string and range conflicts.
    """

    resource_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="The single resource being 'booked'."
    )

    temporal_range = DateTimeRangeField(
        null=True,
        blank=True,
        help_text="[start, end) time interval of the booking."
    )

    integer_range = IntegerRangeField(
        null=True,
        blank=True,
        help_text="[floor, ceiling] integer or other numeric range."
    )

    arbitrary_dims = models.JSONField(
        null=True,
        blank=True,
        help_text="For arbitrary key/value checks"
    )

    source_app = models.CharField(
        max_length=100,
        db_index=True
    )
    source_object_id = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["source_app", "source_object_id"]),

            GistIndex(
                fields=["temporal_range"], 
                name="ix_conflict_temporal_gist"
            ),

            GistIndex(
                fields=["integer_range"],
                name="ix_conflict_integer_gist"
            ),
        ]

    def __str__(self):
        return f"ConflictItem: {self.source_app} - {self.resource_id}"
