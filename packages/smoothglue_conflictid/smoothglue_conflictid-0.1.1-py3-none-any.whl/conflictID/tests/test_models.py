import pytest
from datetime import datetime
from django.utils.timezone import make_aware
from conflictID.models import ConflictItem


@pytest.mark.django_db
class TestConflictItemModel:

    def test_create_conflict_item(self):
        """
        Test basic creation of a ConflictItem.
        """
        start_time = make_aware(datetime(2025, 11, 10, 9, 0))
        end_time = make_aware(datetime(2025, 11, 10, 10, 0))

        item = ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="res-123",
            resource_id="equipment-abc",
            temporal_range=(start_time, end_time),
            integer_range=(100, 200),
            arbitrary_dims={"key": "value"}
        )

        item.refresh_from_db()

        assert item.pk is not None
        assert item.resource_id == "equipment-abc"
        assert item.source_app == "scheduling_app"
        assert item.integer_range.lower == 100
        assert item.temporal_range.upper == end_time
        assert item.arbitrary_dims["key"] == "value"

    def test_conflict_item_str_method(self):
        """
        Test the __str__ method for a human-readable representation.
        """
        item = ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="res-456",
            resource_id="equipment-xyz",
        )

        expected_str = "ConflictItem: scheduling_app - equipment-xyz"
        assert str(item) == expected_str

    def test_conflict_item_minimal_creation(self):
        """
        Test that an item can be created with only the required fields.
        """
        item = ConflictItem.objects.create(
            source_app="scheduling_app",
            source_object_id="res-789",
            resource_id="equipment-minimal",
        )

        assert item.pk is not None
        assert item.resource_id == "equipment-minimal"
        assert item.temporal_range is None
        assert item.integer_range is None
        assert item.arbitrary_dims is None
