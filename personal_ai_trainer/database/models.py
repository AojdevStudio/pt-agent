"""
Database model definitions for the Personal AI Training Agent.

Defines base and entity models for user profiles, workout plans, logs,
readiness metrics, and the knowledge base.
"""

from typing import List, Optional, ClassVar
from datetime import date
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Base model for all database entities.
    Provides serialization and validation.
    """
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    """
    Represents a user profile in the system.
    """
    user_id: str
    name: str
    age: int
    height: float  # in centimeters
    weight: float  # in kilograms
    fitness_level: Optional[str] = None
    goals: Optional[str] = None
    preferences: Optional[str] = None


class WorkoutPlan(BaseModel):
    """
    Represents a workout plan for a user.
    """
    plan_id: str
    user_id: str
    week_number: int
    start_date: date
    end_date: date
    readiness_adjustment: Optional[float] = None
    status: Optional[str] = None


class Workout(BaseModel):
    """
    Represents a single workout session.
    """
    workout_id: str
    plan_id: str
    day_number: int
    date: date
    focus_area: Optional[str] = None
    readiness_score: Optional[float] = None
    completed: bool = False
    notes: Optional[str] = None


class Exercise(BaseModel):
    """
    Represents an exercise within a workout.
    """
    exercise_id: str
    workout_id: str
    name: str
    sets: int
    reps: int
    load: Optional[float] = None  # in kilograms
    rpe: Optional[float] = None   # Rate of Perceived Exertion
    completed: bool = False
    actual_load: Optional[float] = None
    actual_reps: Optional[int] = None


class ReadinessMetrics(BaseModel):
    """
    Represents daily readiness and recovery metrics for a user.
    """
    metrics_id: str
    user_id: str
    date: date
    hrv: Optional[float] = None
    sleep_score: Optional[float] = None
    recovery_score: Optional[float] = None
    readiness_score: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[float] = None


class KnowledgeBase(BaseModel):
    """
    Represents a knowledge base document with vector embedding.
    """
    document_id: str
    title: str
    content: str
    embedding: List[float] = Field(default_factory=list, description="Vector embedding for pgvector")
    category: Optional[str] = None
    source: Optional[str] = None
    date_added: Optional[date] = None