"""Detect duplicate or overlapping activities based on time windows."""

from datetime import timedelta

from app.models.activity import Activity
from app.schemas.activity import DuplicateCandidate


async def find_duplicates(new_activity: Activity, user_id: str) -> list[DuplicateCandidate]:
    """
    Find existing activities that overlap with the new activity.
    Overlap is detected by comparing start/end time windows.
    Also checks file hash for exact duplicates.
    """
    duplicates: list[DuplicateCandidate] = []

    # Check exact hash match first
    if new_activity.file_hash:
        exact_match = await Activity.find_one(
            Activity.user_id == user_id,
            Activity.file_hash == new_activity.file_hash,
        )
        if exact_match:
            duplicates.append(
                DuplicateCandidate(
                    existing_id=str(exact_match.id),
                    existing_name=exact_match.name,
                    existing_start=exact_match.start_time,
                    existing_end=exact_match.end_time,
                    new_start=new_activity.start_time,
                    new_end=new_activity.end_time,
                    overlap_seconds=new_activity.total_timer_time,
                )
            )
            return duplicates

    # Check time-based overlap
    # Use a tolerance of 5 minutes on each side
    tolerance = timedelta(minutes=5)
    new_start = new_activity.start_time - tolerance
    new_end = (new_activity.end_time or new_activity.start_time) + tolerance

    overlapping = await Activity.find(
        Activity.user_id == user_id,
        Activity.start_time <= new_end,
        Activity.end_time >= new_start,
    ).to_list()

    for existing in overlapping:
        # Calculate overlap duration
        overlap_start = max(new_activity.start_time, existing.start_time)
        overlap_end = min(
            new_activity.end_time or new_activity.start_time,
            existing.end_time or existing.start_time,
        )
        overlap_seconds = max(0, (overlap_end - overlap_start).total_seconds())

        if overlap_seconds > 60:  # At least 1 minute of overlap
            duplicates.append(
                DuplicateCandidate(
                    existing_id=str(existing.id),
                    existing_name=existing.name,
                    existing_start=existing.start_time,
                    existing_end=existing.end_time,
                    new_start=new_activity.start_time,
                    new_end=new_activity.end_time,
                    overlap_seconds=overlap_seconds,
                )
            )

    return duplicates
