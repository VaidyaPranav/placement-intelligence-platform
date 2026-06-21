# Pydantic Schemas for Company Intelligence Agent

from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ExperienceLevelEnum(str, Enum):
    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry Level"
    JUNIOR = "Junior"
    MID_LEVEL = "Mid Level"
    SENIOR = "Senior"


class SkillEvidence(BaseModel):
    skill_tag: str = Field(description="The extracted skill keyword (normalized).")
    evidence_sentence: str = Field(
        description="The exact sentence from the job description where this skill was mentioned."
    )


class ExplainabilitySection(BaseModel):
    role_evidence: str = Field(
        description="Sentence from the job description indicating the job role/title."
    )
    skill_evidence: List[SkillEvidence] = Field(
        description="List of skill keywords mapped to their supporting sentences."
    )
    cgpa_evidence: str = Field(
        description="Sentence from the job description indicating grade or CGPA requirements. Use 'Not Specified' if missing."
    )


class CompanyIntelligenceOutput(BaseModel):
    job_id: UUID = Field(description="Unique UUID identifier for this job description.")
    role_title: str = Field(description="Extracted official job title.")
    role_category: str = Field(
        description="The normalized category of the role (e.g., Software Engineering, Data & Analytics, AI/ML, Cloud & DevOps)."
    )
    experience_level: ExperienceLevelEnum = Field(
        description="Mapped experience bracket required for the role."
    )
    required_skills: List[str] = Field(
        description="Core mandatory technical skills required for the role."
    )
    preferred_skills: List[str] = Field(
        description="Optional or preferred skills that are nice-to-have."
    )
    soft_skills: List[str] = Field(
        description="Non-technical skills (e.g., communication, teamwork, leadership)."
    )
    minimum_cgpa: float = Field(
        default=0.0,
        description="Minimum CGPA/GPA requirement scaled to a 10.0 max. Defaults to 0.0 if not specified.",
    )
    extraction_method: Optional[str] = Field(default=None, description="The method of extraction used ('llm' or 'fallback').")
    overall_confidence: float = Field(
        description="Overall confidence score for the extraction (0.0 to 1.0)."
    )
    skill_confidence: float = Field(
        description="Confidence score for skill extraction (0.0 to 1.0)."
    )
    role_confidence: float = Field(
        description="Confidence score for role extraction (0.0 to 1.0)."
    )
    cgpa_confidence: float = Field(
        description="Confidence score for CGPA extraction (0.0 to 1.0)."
    )
    explainability_section: ExplainabilitySection = Field(
        description="Explanations and direct text quotes showing where the information was found."
    )

    @field_validator("minimum_cgpa")
    @classmethod
    def validate_cgpa(cls, v: float) -> float:
        if not (0.0 <= v <= 10.0):
            raise ValueError("CGPA must be between 0.0 and 10.0")
        return v

    @field_validator("overall_confidence", "skill_confidence", "role_confidence", "cgpa_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence scores must be between 0.0 and 1.0")
        return v
