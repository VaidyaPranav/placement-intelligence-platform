# Pydantic Schemas for Ranking Agent

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RecommendationEnum(str, Enum):
    STRONG_MATCH = "STRONG_MATCH"
    GOOD_MATCH = "GOOD_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    WEAK_MATCH = "WEAK_MATCH"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class MatchResult(BaseModel):
    student_id: UUID = Field(description="Unique UUIDv4 identifier of the student.")
    job_id: UUID = Field(description="Unique UUIDv4 identifier of the job description.")
    match_score: float = Field(description="The calculated match score (0.0 to 100.0).")
    matched_skills: list[str] = Field(description="List of required skills matched.")
    missing_skills: list[str] = Field(description="List of required skills missing.")
    preferred_skills_matched: list[str] = Field(description="List of preferred skills matched.")
    preferred_skills_missing: list[str] = Field(description="List of preferred skills missing.")
    cgpa_eligible: bool = Field(description="True if student's CGPA matches or exceeds minimum required.")
    recommendation: RecommendationEnum = Field(description="The match recommendation category.")
    reasoning: str = Field(description="Detailed text explaining the score calculation and recommendation.")
    overall_confidence: float = Field(description="The overall confidence score for the analysis (0.0 to 1.0).")
    required_skill_score: float = Field(default=0.0, description="Score contribution from required skills (0.0 to 100.0).")
    preferred_skill_score: float = Field(default=0.0, description="Score contribution from preferred skills (0.0 to 100.0).")
    cgpa_score: float = Field(default=0.0, description="Score contribution from CGPA eligibility (0.0 to 100.0).")

    @field_validator("match_score")
    @classmethod
    def validate_match_score(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("match_score must be between 0.0 and 100.0.")
        return v

    @field_validator("overall_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_confidence must be between 0.0 and 1.0.")
        return v
