from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class WorkoutStep(BaseModel):
    """A single step in a structured workout."""
    step_type: str  # warmup, active, recovery, cooldown, rest
    duration_type: str  # time, distance, calories, open
    duration_value: Optional[float] = None  # seconds, meters, or calories
    target_type: Optional[str] = None  # heart_rate, power, pace, cadence, open
    target_low: Optional[float] = None
    target_high: Optional[float] = None
    notes: Optional[str] = None


class PlannedWorkout(Document):
    user_id: str

    # Schedule
    scheduled_date: datetime
    completed: bool = False
    activity_id: Optional[str] = None  # linked activity when fulfilled

    # Workout definition
    name: str
    description: Optional[str] = None
    sport: str = "other"
    estimated_duration: Optional[float] = None  # seconds
    estimated_tss: Optional[float] = None
    steps: list[WorkoutStep] = Field(default_factory=list)

    # Pre-activity comments (like TrainingPeaks)
    pre_activity_comments: Optional[str] = None
    post_activity_comments: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "planned_workouts"
        indexes = [
            "user_id",
            [("user_id", 1), ("scheduled_date", -1)],
        ]
