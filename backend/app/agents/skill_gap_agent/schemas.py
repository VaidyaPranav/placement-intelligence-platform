# Pydantic Schemas for Skill Gap Agent

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class PriorityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SkillRecommendation(BaseModel):
    skill: str = Field(description="The name of the missing skill.")
    priority: PriorityEnum = Field(description="The study/acquisition priority.")
    recommendation: str = Field(description="Actionable study recommendations.")
    estimated_improvement_score: float = Field(
        description="Estimated matching score improvement once skill is acquired (0.0 to 100.0)."
    )

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("skill cannot be empty.")
        return v.strip()

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("recommendation cannot be empty.")
        return v.strip()

    @field_validator("estimated_improvement_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("estimated_improvement_score must be between 0.0 and 100.0.")
        return v


class SkillGapReport(BaseModel):
    student_id: UUID = Field(description="Unique UUIDv4 identifier of the student.")
    job_id: UUID = Field(description="Unique UUIDv4 identifier of the job.")
    gap_score: float = Field(description="The calculated skill gap score (0.0 to 100.0).")
    missing_required_skills: list[str] = Field(description="List of missing required skills.")
    missing_preferred_skills: list[str] = Field(description="List of missing preferred skills.")
    severity: SeverityEnum = Field(description="The severity level of the gap.")
    recommendations: list[SkillRecommendation] = Field(description="Actionable skill acquisition recommendations.")
    overall_confidence: float = Field(description="Overall extraction confidence score (0.0 to 1.0).")

    @field_validator("gap_score")
    @classmethod
    def validate_gap_score(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("gap_score must be between 0.0 and 100.0.")
        return v

    @field_validator("overall_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_confidence must be between 0.0 and 1.0.")
        return v
