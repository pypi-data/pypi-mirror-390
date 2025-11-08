import pytest
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from conflictID.models import ConflictItem
from conflictID.queries import DeconflictionQuery


def dt(day, hour, minute=0, second=0):
    """
    Helper to create aware datetimes
    """
    return make_aware(datetime(2025, 11, day, hour, minute, second))


@pytest.mark.django_db
class TestDeconflictionQuery:

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Creates a set of initial data to query against.
        """
        # An existing 1-hour reservation for "equipment_123"
        ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="existing_1",
            resource_id="equipment_123",
            temporal_range=(dt(10, 9), dt(10, 10))  # 9:00 - 10:00
        )

        # A 2-hour reservation for a *different* piece of equipment
        ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="existing_2",
            resource_id="equipment_456",
            temporal_range=(dt(10, 9), dt(10, 11))  # 9:00 - 11:00
        )

        # A reservation for the same equipment, but on a different day
        ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="existing_3",
            resource_id="equipment_123",
            temporal_range=(dt(11, 9), dt(11, 10))  # Next day, 9:00 - 10:00
        )

    def test_scheduling_direct_conflict(self):
        """
        Check for "string match" (resource_id) + "range overlap" (temporal_range)

        Proposed Item: equipment_123 @ 9:30 - 10:30
        This should conflict with existing_1 (9:00 - 10:00)
        """
        query = (
            DeconflictionQuery()
            .with_resource_id("equipment_123")
            .with_temporal_overlap(dt(10, 9, 30), dt(10, 10, 30))  # This will now work
            .exclude_self(source_app="scheduling_app", source_object_id="new_item")
        )

        conflicts = query.execute()

        assert conflicts.count() == 1
        assert conflicts.first().source_object_id == "existing_1"

    def test_scheduling_no_conflict_different_resource(self):
        """
        Check for "string match" (resource_id) + "range overlap" (temporal_range)

        Proposed Item: equipment_789 @ 9:30 - 10:30
        This overlaps in time with existing_1 and existing_2, but for a
        *different resource*. It should NOT find a conflict.
        """
        query = (
            DeconflictionQuery()
            .with_resource_id("equipment_789") # New resource
            .with_temporal_overlap(dt(10, 9, 30), dt(10, 10, 30))  # This will now work
            .exclude_self(source_app="scheduling_app", source_object_id="new_item")
        )

        conflicts = query.execute()

        assert conflicts.count() == 0

    def test_scheduling_no_conflict_different_time(self):
        """
        Check for "string match" (resource_id) + "range overlap" (temporal_range)

        Proposed Item: equipment_123 @ 14:00 - 15:00
        This is for the *same resource* as existing_1, but at a
        *different time*. It should NOT find a conflict.
        """
        query = (
            DeconflictionQuery()
            .with_resource_id("equipment_123")
            .with_temporal_overlap(dt(10, 14), dt(10, 15))
            .exclude_self(source_app="scheduling_app", source_object_id="new_item")
        )

        conflicts = query.execute()

        assert conflicts.count() == 0

    def test_exclude_self(self):
        """
        Test that the query correctly excludes the item being edited.

        Proposed Item: We are *editing* existing_1 (equipment_123 @ 9:00 - 10:00)
        We are checking its *own* data against the database.
        It should not find a conflict with itself.
        """
        query = (
            DeconflictionQuery()
            .with_resource_id("equipment_123")
            .with_temporal_overlap(dt(10, 9), dt(10, 10))
            .exclude_self(source_app="scheduling_app", source_object_id="existing_1")
        )

        conflicts = query.execute()

        assert conflicts.count() == 0
