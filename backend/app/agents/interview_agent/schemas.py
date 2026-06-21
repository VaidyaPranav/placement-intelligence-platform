# Pydantic Schemas for Interview Agent

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class DifficultyEnum(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question.")
    skill: str = Field(description="The skill category of the question.")
    difficulty: DifficultyEnum = Field(description="The difficulty level.")
    expected_answer_keywords: list[str] = Field(description="Expected keywords in the response.")
    evaluation_rubric: list[str] = Field(description="Rubric for evaluating response criteria.")

    @field_validator("question", "skill")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("String fields must not be empty.")
        return v.strip()

    @field_validator("expected_answer_keywords", "evaluation_rubric")
    @classmethod
    def validate_non_empty_list(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("List must contain at least 1 item.")
        # Ensure no empty strings
        for item in v:
            if not item or not item.strip():
                raise ValueError("List items must not be empty.")
        return [item.strip() for item in v]


class InterviewPreparationReport(BaseModel):
    student_id: UUID = Field(description="Unique UUIDv4 identifier of the student.")
    job_id: UUID = Field(description="Unique UUIDv4 identifier of the job.")
    role_title: str = Field(description="Target role title.")
    technical_questions: list[InterviewQuestion] = Field(description="Ordered list of technical questions.")
    behavioral_questions: list[InterviewQuestion] = Field(description="List of behavioral questions.")
    weak_area_questions: list[InterviewQuestion] = Field(description="Questions targeting candidate's weak areas.")
    strong_area_questions: list[InterviewQuestion] = Field(description="Questions targeting candidate's strong areas.")
    focus_areas: list[str] = Field(description="Primary skills requiring interview preparation.")
    overall_difficulty: DifficultyEnum = Field(description="Overall difficulty level based on match score recommendation.")
    estimated_interview_readiness_score: float = Field(description="Estimated interview readiness score (0.0 to 100.0).")
    overall_confidence: float = Field(description="Overall extraction/generation confidence score (0.0 to 1.0).")
    interview_pack_version: str = Field(default="1.0.0", description="Version of the interview preparation pack.")
    generated_from_match_score: float = Field(description="Original MatchResult match_score.")
    preparation_summary: str = Field(description="Human-readable prep summary.")

    @field_validator("role_title", "interview_pack_version", "preparation_summary")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("String fields must not be empty.")
        return v.strip()

    @field_validator("estimated_interview_readiness_score", "generated_from_match_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("Scores must be between 0.0 and 100.0.")
        return v

    @field_validator("overall_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("overall_confidence must be between 0.0 and 1.0.")
        return v
