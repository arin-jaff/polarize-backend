from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class RecordPoint(BaseModel):
    """A single time-series data point from a FIT file."""
    timestamp: datetime
    heart_rate: Optional[int] = None
    power: Optional[int] = None
    cadence: Optional[int] = None
    speed: Optional[float] = None  # m/s
    distance: Optional[float] = None  # meters cumulative
    altitude: Optional[float] = None  # meters
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    temperature: Optional[float] = None


class LapSummary(BaseModel):
    """Summary of a single lap."""
    start_time: datetime
    total_timer_time: float  # seconds
    total_distance: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    avg_power: Optional[int] = None
    max_power: Optional[int] = None
    avg_cadence: Optional[int] = None
    avg_speed: Optional[float] = None


class Activity(Document):
    user_id: str
    source: str = "upload"  # upload, garmin, concept2

    # Identity & dedup
    original_filename: Optional[str] = None
    source_id: Optional[str] = None  # external ID from Garmin/Concept2
    file_hash: Optional[str] = None  # SHA256 of uploaded file for dedup

    # Core metadata
    sport: str = "other"  # rowing, cycling, running, swimming, strength, other
    sub_sport: Optional[str] = None  # indoor_rowing, road, trail, etc.
    name: Optional[str] = None
    description: Optional[str] = None

    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    total_timer_time: float  # seconds (moving time)
    total_elapsed_time: Optional[float] = None  # seconds (total including stops)

    # Summaries
    total_distance: Optional[float] = None  # meters
    total_calories: Optional[int] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    avg_power: Optional[int] = None
    max_power: Optional[int] = None
    normalized_power: Optional[float] = None  # NP
    avg_cadence: Optional[int] = None
    avg_speed: Optional[float] = None  # m/s
    max_speed: Optional[float] = None
    total_ascent: Optional[float] = None
    total_descent: Optional[float] = None
    avg_stroke_rate: Optional[int] = None  # for rowing

    # Computed metrics
    tss: Optional[float] = None  # Training Stress Score
    intensity_factor: Optional[float] = None  # IF = NP / FTP
    scaled_tss: Optional[float] = None  # TSS after sport scaling

    # Time-series data (stored for graphing, combining)
    records: list[RecordPoint] = Field(default_factory=list)
    laps: list[LapSummary] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_combined: bool = False  # True if this activity was created by combining files
    combined_from: list[str] = Field(default_factory=list)  # Activity IDs combined

    class Settings:
        name = "activities"
        indexes = [
            "user_id",
            "start_time",
            [("user_id", 1), ("start_time", -1)],
        ]
