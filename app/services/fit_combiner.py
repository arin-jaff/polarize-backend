"""Combine two overlapping FIT file activities into one."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.models.activity import Activity, RecordPoint


async def combine_activities(
    activity_id_1: str,
    activity_id_2: str,
    user_id: str,
    time_offset_ms: int = 0,
    prefer_data_from: int = 1,
) -> Activity:
    """
    Combine two activities into a single merged activity.

    Args:
        activity_id_1: First activity ID
        activity_id_2: Second activity ID
        user_id: Owner user ID
        time_offset_ms: Manual time alignment offset in milliseconds
                        (applied to activity_2 timestamps)
        prefer_data_from: Which activity's data to prefer for conflicts (1 or 2)
    """
    act1 = await Activity.get(activity_id_1)
    act2 = await Activity.get(activity_id_2)

    if not act1 or act1.user_id != user_id:
        raise HTTPException(status_code=404, detail=f"Activity {activity_id_1} not found")
    if not act2 or act2.user_id != user_id:
        raise HTTPException(status_code=404, detail=f"Activity {activity_id_2} not found")

    # Apply time offset to activity 2's records
    offset = timedelta(milliseconds=time_offset_ms)
    records_2 = []
    for r in act2.records:
        adjusted = r.model_copy()
        adjusted.timestamp = r.timestamp + offset
        records_2.append(adjusted)

    # Merge records by timestamp
    merged_records = _merge_records(act1.records, records_2, prefer_data_from)

    # Compute merged summary stats
    start_time = min(act1.start_time, act2.start_time + offset)
    end_time = max(
        act1.end_time or act1.start_time,
        (act2.end_time or act2.start_time) + offset,
    )
    total_timer_time = (end_time - start_time).total_seconds()

    # Build combined activity
    combined = Activity(
        user_id=user_id,
        source="combined",
        sport=act1.sport,
        sub_sport=act1.sub_sport,
        name=f"Combined: {act1.name or 'Activity 1'} + {act2.name or 'Activity 2'}",
        start_time=start_time,
        end_time=end_time,
        total_timer_time=total_timer_time,
        total_elapsed_time=total_timer_time,
        records=merged_records,
        laps=act1.laps + act2.laps,  # concatenate laps
        is_combined=True,
        combined_from=[str(act1.id), str(act2.id)],
    )

    # Recompute summary stats from merged records
    _compute_summary_from_records(combined)

    return combined


def _merge_records(
    records_1: list[RecordPoint],
    records_2: list[RecordPoint],
    prefer: int = 1,
) -> list[RecordPoint]:
    """
    Merge two lists of record points by timestamp.
    When timestamps overlap (within 1 second), merge fields preferring
    data from the specified source.
    """
    # Index records by rounded timestamp (to nearest second)
    by_time: dict[int, RecordPoint] = {}

    # Add records from the non-preferred source first
    secondary = records_2 if prefer == 1 else records_1
    primary = records_1 if prefer == 1 else records_2

    for r in secondary:
        ts_key = int(r.timestamp.timestamp())
        by_time[ts_key] = r.model_copy()

    # Overlay with preferred source (overwrites conflicting fields)
    for r in primary:
        ts_key = int(r.timestamp.timestamp())
        if ts_key in by_time:
            existing = by_time[ts_key]
            # Merge: prefer primary for non-None fields
            merged = existing.model_copy()
            for field_name in RecordPoint.model_fields:
                primary_val = getattr(r, field_name)
                if primary_val is not None:
                    setattr(merged, field_name, primary_val)
            by_time[ts_key] = merged
        else:
            by_time[ts_key] = r.model_copy()

    # Sort by timestamp
    return sorted(by_time.values(), key=lambda r: r.timestamp)


def _compute_summary_from_records(activity: Activity) -> None:
    """Recompute summary statistics from merged record data."""
    if not activity.records:
        return

    hrs = [r.heart_rate for r in activity.records if r.heart_rate is not None]
    powers = [r.power for r in activity.records if r.power is not None]
    cadences = [r.cadence for r in activity.records if r.cadence is not None]
    speeds = [r.speed for r in activity.records if r.speed is not None]
    altitudes = [r.altitude for r in activity.records if r.altitude is not None]

    if hrs:
        activity.avg_heart_rate = round(sum(hrs) / len(hrs))
        activity.max_heart_rate = max(hrs)
    if powers:
        activity.avg_power = round(sum(powers) / len(powers))
        activity.max_power = max(powers)
    if cadences:
        activity.avg_cadence = round(sum(cadences) / len(cadences))
    if speeds:
        activity.avg_speed = sum(speeds) / len(speeds)
        activity.max_speed = max(speeds)

    # Distance from last record
    distances = [r.distance for r in activity.records if r.distance is not None]
    if distances:
        activity.total_distance = max(distances)

    # Elevation
    if altitudes and len(altitudes) > 1:
        ascent = 0.0
        descent = 0.0
        for i in range(1, len(altitudes)):
            diff = altitudes[i] - altitudes[i - 1]
            if diff > 0:
                ascent += diff
            else:
                descent += abs(diff)
        activity.total_ascent = round(ascent, 1)
        activity.total_descent = round(descent, 1)


def get_overlay_data(act1: Activity, act2: Activity, time_offset_ms: int = 0) -> dict:
    """
    Get overlay data for the visual alignment UI.
    Returns time-series data from both activities for HR, power, and speed.
    """
    offset = timedelta(milliseconds=time_offset_ms)

    def extract_series(records: list[RecordPoint], base_time: datetime, apply_offset=False):
        series = {"time_s": [], "heart_rate": [], "power": [], "speed": []}
        for r in records:
            ts = r.timestamp
            if apply_offset:
                ts = ts + offset
            elapsed = (ts - base_time).total_seconds()
            series["time_s"].append(elapsed)
            series["heart_rate"].append(r.heart_rate)
            series["power"].append(r.power)
            series["speed"].append(r.speed)
        return series

    base_time = min(act1.start_time, act2.start_time)

    return {
        "file_1": {
            "name": act1.name or act1.original_filename,
            "data": extract_series(act1.records, base_time),
        },
        "file_2": {
            "name": act2.name or act2.original_filename,
            "data": extract_series(act2.records, base_time, apply_offset=True),
        },
    }
