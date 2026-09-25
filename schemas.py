from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


class ExerciseItem(BaseModel):
    name: str = Field(..., description="Name of the exercise")
    sets: Optional[str] = Field("3 sets", description="Number of sets")
    reps: Optional[str] = Field("10-12 reps", description="Repetitions or duration")
    rest: Optional[str] = Field("60s", description="Rest time between sets")
    notes: Optional[str] = Field("", description="Form tips or execution notes")


class DayWorkout(BaseModel):
    day: int = Field(..., ge=1, le=7, description="Day number 1 to 7")
    title: str = Field(..., description="Day title e.g. Day 1 - Upper Body Blast")
    focus: str = Field(..., description="Primary focus or muscle group")
    is_rest_day: bool = Field(False, description="Whether this day is a dedicated rest/recovery day")
    warm_up: str = Field("5-10 minutes dynamic stretching", description="Warm-up routine")
    exercises: List[ExerciseItem] = Field(default_factory=list, description="List of exercises")
    cool_down: str = Field("5 minutes static stretching & hydration", description="Cool-down routine")


class WorkoutPlanStructure(BaseModel):
    plan_title: str = Field("7-Day Personalized AI Workout Plan", description="Plan title")
    summary: str = Field("Personalized fitness roadmap tailored to your goals.", description="Plan summary")
    days: List[DayWorkout] = Field(..., description="7 day schedule")
    nutrition_tip: str = Field(..., description="Goal-specific nutrition and recovery recommendation")
    disclaimer: str = Field(
        "This information is for general wellness and educational purposes and is not a substitute for professional medical or nutritional advice.",
        description="Health safety disclaimer"
    )


class UserProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    user_id: str = Field(..., min_length=3, max_length=50, description="Unique User Identifier")
    age: int = Field(..., ge=13, le=120, description="Age in years (13-120)")
    weight: float = Field(..., ge=20.0, le=350.0, description="Weight in kilograms (20-350)")
    goal: str = Field(..., description="Fitness Goal")
    intensity: str = Field(..., description="Workout Intensity")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty.")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise ValueError("User ID must contain only letters, numbers, hyphens, and underscores.")
        return v

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str) -> str:
        valid_goals = ["Weight Loss", "Muscle Gain", "General Wellness", "Flexibility", "Endurance"]
        # Case-insensitive match to canonical
        for vg in valid_goals:
            if v.strip().lower() == vg.lower():
                return vg
        return v.strip()

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: str) -> str:
        valid_intensities = ["Low", "Medium", "High"]
        for vi in valid_intensities:
            if v.strip().lower() == vi.lower():
                return vi
        return v.strip()


class FeedbackSubmission(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    feedback: str = Field(..., min_length=3, max_length=1000, description="User feedback to modify plan")

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Feedback cannot be empty.")
        return v


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
