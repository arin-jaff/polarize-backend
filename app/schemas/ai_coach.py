"""
AI Coach Schemas

Pydantic models for AI coach API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Request Schemas ---


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    """Basic chat request."""
    message: str
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class PlanModificationRequest(BaseModel):
    """
    Request for AI to analyze and modify the training plan.

    The user provides feedback about how they're feeling, and the AI
    suggests modifications to upcoming workouts.
    """
    feedback: str = Field(
        ...,
        description="User feedback about how they're feeling (fatigue, injury, RPE, etc.)",
        examples=[
            "I'm feeling really tired after yesterday's hard workout, RPE was 9",
            "My knee has been bothering me, might need to avoid running",
            "Feeling great and fresh, ready for a hard session",
        ],
    )
    days_forward: int = Field(
        default=14,
        ge=1,
        le=30,
        description="How many days of workouts to consider",
    )
    previous_suggestions: Optional[list[dict]] = Field(
        default=None,
        description="Previous AI suggestions if user is requesting refinements",
    )


class WeeklyPlanRequest(BaseModel):
    """Request for AI to generate a new weekly training plan."""
    goals: str = Field(
        ...,
        description="Training goals for this week",
        examples=[
            "Build aerobic base, focus on long steady rows",
            "Peak for a 2K erg test on Saturday",
            "Recovery week after a race",
        ],
    )
    constraints: Optional[str] = Field(
        default=None,
        description="Any constraints or preferences",
        examples=[
            "Can only train mornings Mon-Fri",
            "No access to rowing machine Tuesday",
            "Keep total hours under 8",
        ],
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Start date for the plan (defaults to next Monday)",
    )


class ApplyModificationsRequest(BaseModel):
    """Request to apply AI-suggested modifications."""
    response_json: dict = Field(
        ...,
        description="The parsed JSON response from the AI",
    )
    dry_run: bool = Field(
        default=False,
        description="If true, validate but don't commit changes",
    )


class RefineRequest(BaseModel):
    """Request for refining previous AI suggestions."""
    original_response: dict = Field(
        ...,
        description="The original AI response to refine",
    )
    refinement_feedback: str = Field(
        ...,
        description="User feedback on what to change",
        examples=[
            "Keep the first modification but make Saturday's workout harder",
            "I don't want to skip Thursday, just make it easier",
            "Add a swim workout on Wednesday instead",
        ],
    )


class CoachSettingsUpdate(BaseModel):
    """Request to update coach settings."""
    coach_type: Optional[str] = Field(
        default=None,
        description="Coach type: specialist, generalist, recreational",
    )
    training_plan: Optional[str] = Field(
        default=None,
        description="Training plan type: polarized, traditional, threshold",
    )
    time_constraint: Optional[str] = Field(
        default=None,
        description="Time constraint: minimal, moderate, committed, serious, elite",
    )
    weekly_hours_available: Optional[float] = Field(
        default=None,
        ge=0,
        le=50,
        description="Specific weekly hours available for training",
    )


class CoachSettingsResponse(BaseModel):
    """Response with current coach settings."""
    coach_type: str
    training_plan: str
    time_constraint: str
    weekly_hours_available: Optional[float] = None


# --- Response Schemas ---


class ChatResponse(BaseModel):
    """Basic chat response."""
    response: str


class WorkoutChangeDetail(BaseModel):
    """Details of a single change to a workout."""
    field: str  # duration, intensity, tss, etc.
    from_value: Optional[str] = None
    to_value: str


class ModificationPreview(BaseModel):
    """Preview of a single modification."""
    type: str  # modification, new_workout, skip
    action: Optional[str] = None
    workout_id: Optional[str] = None
    date: str
    original_name: Optional[str] = None
    new_name: Optional[str] = None
    sport: Optional[str] = None
    duration_minutes: Optional[float] = None
    estimated_tss: Optional[float] = None
    details: Optional[dict] = None
    notes: Optional[str] = None


class LoadAdjustment(BaseModel):
    """Weekly load adjustment summary."""
    current_weekly_tss: Optional[float] = None
    recommended_weekly_tss: Optional[float] = None
    reason: Optional[str] = None


class PlanModificationResponse(BaseModel):
    """Response containing AI's plan modifications."""
    success: bool
    summary: Optional[str] = None
    athlete_message: Optional[str] = None
    modifications: list[ModificationPreview] = Field(default_factory=list)
    load_adjustment: Optional[LoadAdjustment] = None
    raw_response: dict = Field(
        ...,
        description="The raw parsed JSON from the AI for later application",
    )
    errors: list[str] = Field(default_factory=list)


class ApplyModificationsResponse(BaseModel):
    """Response after applying modifications."""
    success: bool
    modified_workouts: list[str] = Field(default_factory=list)
    created_workouts: list[str] = Field(default_factory=list)
    skipped_workouts: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class WorkoutFileResponse(BaseModel):
    """Response with workout file download info."""
    workout_id: str
    filename: str
    content_type: str = "application/octet-stream"


# --- Context Schemas (for display) ---


class AthleteContext(BaseModel):
    """Athlete context shown in the UI."""
    name: str
    primary_sport: str
    fitness_ctl: float
    fatigue_atl: float
    form_tsb: float
    form_status: str
    form_description: str


class RecentActivitySummary(BaseModel):
    """Summary of a recent activity."""
    date: str
    sport: str
    name: Optional[str] = None
    duration_minutes: float
    tss: Optional[float] = None
    avg_hr_bpm: Optional[int] = None
    np_watts: Optional[float] = None


class UpcomingWorkoutSummary(BaseModel):
    """Summary of an upcoming planned workout."""
    id: str
    date: str
    name: str
    sport: str
    duration_minutes: Optional[float] = None
    estimated_tss: Optional[float] = None
    description: Optional[str] = None


class CoachingContext(BaseModel):
    """Full coaching context response."""
    athlete: AthleteContext
    recent_activities: list[RecentActivitySummary] = Field(default_factory=list)
    upcoming_workouts: list[UpcomingWorkoutSummary] = Field(default_factory=list)
