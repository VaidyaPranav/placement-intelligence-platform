# Pydantic Schemas for Career Roadmap Agent

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from backend.app.agents.skill_gap_agent.schemas import SeverityEnum


class DifficultyEnum(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class RoadmapTask(BaseModel):
    week_number: int = Field(description="The week number of this task.")
    skill: str = Field(description="The name of the skill being learned.")
    title: str = Field(description="The title of the task.")
    description: str = Field(description="Description of the learning task.")
    estimated_hours: float = Field(description="Estimated hours required.")
    difficulty: DifficultyEnum = Field(description="The difficulty level of the task.")

    @field_validator("week_number")
    @classmethod
    def validate_week_number(cls, v: int) -> int:
        if v < 1:
            raise ValueError("week_number must be at least 1.")
        return v

    @field_validator("estimated_hours")
    @classmethod
    def validate_hours(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("estimated_hours must be greater than 0.")
        return v

    @field_validator("skill", "title", "description")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("String fields must not be empty.")
        return v.strip()


class RoadmapWeek(BaseModel):
    week_number: int = Field(description="The week number.")
    tasks: list[RoadmapTask] = Field(description="The list of tasks for the week.")

    @field_validator("week_number")
    @classmethod
    def validate_week_number(cls, v: int) -> int:
        if v < 1:
            raise ValueError("week_number must be at least 1.")
        return v


class CareerRoadmap(BaseModel):
    student_id: UUID = Field(description="Unique UUIDv4 identifier of the student.")
    total_weeks: int = Field(description="Total duration of the roadmap in weeks.")
    roadmap_weeks: list[RoadmapWeek] = Field(description="Weekly roadmap schedule.")
    expected_match_score_improvement: float = Field(
        description="Expected matching score improvement once roadmap is completed (0.0 to 100.0)."
    )
    overall_confidence: float = Field(
        description="Overall confidence in the roadmap generation (0.0 to 1.0)."
    )
    roadmap_version: str = Field(
        default="1.0.0",
        description="Roadmap schema version."
    )
    generated_from_severity: SeverityEnum = Field(
        description="The SkillGapReport severity used to generate the roadmap."
    )
    roadmap_summary: str = Field(
        description="Human-readable explanation of the roadmap."
    )

    @field_validator("total_weeks")
    @classmethod
    def validate_total_weeks(cls, v: int) -> int:
        if not (1 <= v <= 4):
            raise ValueError("total_weeks must be between 1 and 4.")
        return v

    @field_validator("expected_match_score_improvement")
    @classmethod
    def validate_expected_match_score_improvement(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("expected_match_score_improvement must be between 0.0 and 100.0.")
        return v

    @field_validator("overall_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_confidence must be between 0.0 and 1.0.")
        return v

    @field_validator("roadmap_version", "roadmap_summary")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("String fields must not be empty.")
        return v.strip()
