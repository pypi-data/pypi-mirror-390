from .models import ConflictItem
from django.db import transaction


def sync_item(item_data: dict, delete: bool = False):
    """
    Creates, updates, or deletes a single ConflictItem.

    This is intended to be called from the host app's
    model.save() and model.delete() methods.

    :param item_data: A dict formatted for ConflictItem fields
                      (e.g., from a 'to_conflict_item_dict()' method)
    :param delete: If True, deletes the item instead of upserting.
    """
    if "source_app" not in item_data or "source_object_id" not in item_data:
        raise ValueError("item_data must contain 'source_app' and 'source_object_id'")

    lookup_keys = {
        "source_app": item_data["source_app"],
        "source_object_id": item_data["source_object_id"],
    }

    if delete:
        ConflictItem.objects.filter(**lookup_keys).delete()
    else:
        ConflictItem.objects.update_or_create(
            **lookup_keys,
            defaults=item_data
        )


def sync_items_bulk(items_data: list[dict], update_only: bool = False):
    """
    Bulk creates or updates a list of ConflictItems.

    This is intended to be called from the host app's
    custom ModelManager (e.g., from bulk_create() or bulk_update()).

    :param items_data: A list of dicts for ConflictItem
    :param update_only: If True, performs a bulk_update. If False,
                        performs a bulk_create (default).
    """
    if not items_data:
        return

    if update_only:
        # bulk_update is more complex and requires matching pks
        # or using 'update_conflicts=True' on newer Django/Postgres
        # This is a simple (but not fully optimized) implementation:
        with transaction.atomic():
            for item in items_data:
                # Fall back to single-item sync for updates
                sync_item(item)
    else:
        # Handle bulk_create
        conflict_items = [ConflictItem(**data) for data in items_data]
        ConflictItem.objects.bulk_create(conflict_items, ignore_conflicts=True)

    # NOTE: A more robust 'sync_items_bulk' for updates would involve
    # bulk_create(..., update_conflicts=True, update_fields=[...])
    # on Postgres, but that requires more setup. This is a safe
    # starting point.
