from rest_framework import serializers
from .models import ConflictItem


class RangeField(serializers.Field):
    """
    Custom serializer field to correctly format
    PostgreSQL's range objects into a nested JSON object.
    """
    def to_representation(self, value):
        # If the range is None (e.g., integer_range), return None
        if not value:
            return None

        # Check if lower/upper bounds exist and format them
        # This handles both datetimes (with .isoformat()) and integers (which are returned as-is)
        lower = value.lower
        if hasattr(lower, 'isoformat'):
            lower = lower.isoformat()

        upper = value.upper
        if hasattr(upper, 'isoformat'):
            upper = upper.isoformat()

        # Return a descriptive bounds object
        bounds_obj = {
            "lower_inclusive": value.lower_inc,
            "upper_inclusive": value.upper_inc,
        }

        # Return a proper JSON object
        return {
            "lower": lower,
            "upper": upper,
            "bounds": bounds_obj
        }


class ConflictItemSerializer(serializers.ModelSerializer):
    """
    Serializes a ConflictItem to JSON for the API response.
    """

    temporal_range = RangeField()
    integer_range = RangeField()
    class Meta:
        model = ConflictItem
        fields = [
            "id",
            "resource_id",
            "temporal_range",
            "integer_range",
            "arbitrary_dims",
            "source_app",
            "source_object_id",
        ]
