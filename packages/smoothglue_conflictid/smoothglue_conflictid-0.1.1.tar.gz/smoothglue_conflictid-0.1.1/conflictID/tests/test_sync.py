import pytest
from datetime import datetime
from django.utils.timezone import make_aware
from conflictID.models import ConflictItem
from conflictID.sync import sync_item, sync_items_bulk


@pytest.mark.django_db
class TestSyncHelpers:

    def test_sync_item_create(self):
        """Test that sync_item creates a new ConflictItem."""
        assert ConflictItem.objects.count() == 0

        item_data = {
            "source_app": "scheduling_app",
            "source_object_id": "res_1",
            "resource_id": "equipment_123",
            "temporal_range": (make_aware(datetime(2025, 1, 1, 9)), make_aware(datetime(2025, 1, 1, 10))),
            "integer_range": (100, 200)
        }

        sync_item(item_data)

        assert ConflictItem.objects.count() == 1
        item = ConflictItem.objects.first()
        assert item.resource_id == "equipment_123"
        assert item.integer_range.lower == 100

    def test_sync_item_update(self):
        """Test that sync_item updates an existing ConflictItem."""
        self.test_sync_item_create()  # Create the first item

        item_data = {
            "source_app": "scheduling_app",
            "source_object_id": "res_1",
            "resource_id": "equipment_456",  # Changed resource
            "temporal_range": (make_aware(datetime(2025, 1, 1, 9)), make_aware(datetime(2025, 1, 1, 10))),
            "integer_range": (300, 400)  # Changed range
        }

        sync_item(item_data)

        assert ConflictItem.objects.count() == 1  # Still 1 item
        item = ConflictItem.objects.first()
        assert item.resource_id == "equipment_456"  # Data is updated
        assert item.integer_range.lower == 300

    def test_sync_item_delete(self):
        """Test that sync_item with delete=True removes the item."""
        self.test_sync_item_create()  # Create the first item
        assert ConflictItem.objects.count() == 1

        item_data = {
            "source_app": "scheduling_app",
            "source_object_id": "res_1",
        }

        sync_item(item_data, delete=True)

        assert ConflictItem.objects.count() == 0

    def test_sync_items_bulk_create(self):
        """Test that sync_items_bulk creates multiple items."""
        assert ConflictItem.objects.count() == 0

        items_data = [
            {
                "source_app": "scheduling_app",
                "source_object_id": "res_1",
                "resource_id": "equipment_123",
            },
            {
                "source_app": "scheduling_app",
                "source_object_id": "res_2",
                "resource_id": "equipment_456",
            }
        ]

        sync_items_bulk(items_data)

        assert ConflictItem.objects.count() == 2
