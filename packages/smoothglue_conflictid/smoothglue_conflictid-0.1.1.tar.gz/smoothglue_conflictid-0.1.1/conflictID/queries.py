from django.db.models import Q
from .models import ConflictItem


class DeconflictionQuery:
    """
    A builder class to construct a complex deconfliction query
    against the ConflictItem index.
    """

    def __init__(self):
        self.filters = Q()

    def with_resource_id(self, resource_id: str):
        """Adds a check for an exact resource ID match."""
        if resource_id:
            self.filters &= Q(resource_id=resource_id)
        return self

    def with_temporal_overlap(self, start_time, end_time):
        """Adds a check for an overlapping temporal range."""
        if start_time and end_time:
            # '&&' is the "overlaps" operator for PostgreSQL range fields
            self.filters &= Q(temporal_range__overlap=(start_time, end_time))
        return self

    def with_integer_range_overlap(self, floor, ceiling):
        """Adds a check for an overlapping integer range."""
        if floor is not None and ceiling is not None:
            self.filters &= Q(integer_range__overlap=(floor, ceiling))
        return self

    def with_json_match(self, **kwargs):
        """Adds a check for a key/value match in the JSON field."""
        if kwargs:
            self.filters &= Q(arbitrary_dims__contains=kwargs)
        return self

    def exclude_self(self, source_app: str, source_object_id: str):
        """Excludes the item being checked from the results."""
        if source_app and source_object_id:
            self.filters &= ~Q(
                source_app=source_app,
                source_object_id=source_object_id
            )
        return self

    def execute(self):
        """
        Executes the query and returns the conflicting items.
        """
        if self.filters == Q():
            # Don't run an empty query
            return ConflictItem.objects.none()

        return ConflictItem.objects.filter(self.filters)
