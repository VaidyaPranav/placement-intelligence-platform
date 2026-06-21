# Pydantic Schemas for Student Intelligence Agent

from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DepartmentEnum(str, Enum):
    CS = "CS"
    IT = "IT"
    ECE = "ECE"
    EE = "EE"
    ME = "ME"


class PlacementStatusEnum(str, Enum):
    UNPLACED = "UNPLACED"
    PLACED = "PLACED"
    SNOOZED = "SNOOZED"


class TargetRoleCategoryEnum(str, Enum):
    SOFTWARE_ENGINEERING = "Software Engineering"
    DATA_ANALYTICS = "Data & Analytics"
    AI_ML = "AI/ML"
    CLOUD_DEVOPS = "Cloud & DevOps"


class GitHubVerificationStatusEnum(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"


class Project(BaseModel):
    title: str = Field(description="The title of the project.")
    complexity_score: int = Field(
        description="Complexity score of the project on a scale of 1 to 10."
    )

    @field_validator("complexity_score")
    @classmethod
    def validate_complexity(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("Complexity score must be between 1 and 10.")
        return v


class Certification(BaseModel):
    name: str = Field(description="The name of the certification.")
    issuer: str = Field(description="The issuer of the certification.")


class Internship(BaseModel):
    company: str = Field(description="The name of the company.")
    role: str = Field(description="The internship role.")
    duration_months: int = Field(description="Duration in months (minimum 1).")

    @field_validator("duration_months")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Duration in months must be at least 1.")
        return v


class GitHubAnalysis(BaseModel):
    repo_count: int = Field(default=0, description="The number of repositories.")
    languages: List[str] = Field(default_factory=list, description="Programming languages used.")
    verification_status: GitHubVerificationStatusEnum = Field(
        default=GitHubVerificationStatusEnum.UNVERIFIED,
        description="The verification status of the GitHub profile."
    )


class SkillEvidence(BaseModel):
    skill_tag: str = Field(description="The extracted normalized skill tag.")
    evidence_sentence: str = Field(
        description="The exact sentence from the resume supporting this skill."
    )


class ProjectEvidence(BaseModel):
    project_title: str = Field(description="The title of the project.")
    evidence_sentence: str = Field(
        description="The exact sentence from the resume supporting this project."
    )


class CertificationEvidence(BaseModel):
    certification_name: str = Field(description="The name of the certification.")
    evidence_sentence: str = Field(
        description="The exact sentence from the resume supporting this certification."
    )


class InternshipEvidence(BaseModel):
    internship_company: str = Field(description="The company name of the internship.")
    evidence_sentence: str = Field(
        description="The exact sentence from the resume supporting this internship."
    )


class ExplainabilitySection(BaseModel):
    name_evidence: str = Field(description="Evidence or sentence indicating the student name.")
    department_evidence: str = Field(description="Evidence indicating the department/major.")
    cgpa_evidence: str = Field(description="Evidence indicating the CGPA.")
    skill_evidence: List[SkillEvidence] = Field(
        description="List of skill keywords mapped to their supporting sentences."
    )
    project_evidence: List[ProjectEvidence] = Field(
        description="List of projects mapped to their supporting sentences."
    )
    certification_evidence: List[CertificationEvidence] = Field(
        description="List of certifications mapped to their supporting sentences."
    )
    internship_evidence: List[InternshipEvidence] = Field(
        description="List of internships mapped to their supporting sentences."
    )


class StudentProfile(BaseModel):
    student_id: UUID = Field(description="Unique UUIDv4 identifier for the student.")
    name: str = Field(description="Full name of the student.")
    department: DepartmentEnum = Field(description="Institutional department major.")
    cgpa: float = Field(description="Cumulative Grade Point Average scaled to 10.0.")
    skills: List[str] = Field(description="Unique list of extracted/normalized skills.")
    projects: List[Project] = Field(description="Extracted academic or personal projects.")
    certifications: List[Certification] = Field(description="Extracted professional certifications.")
    achievements: List[str] = Field(description="Extracted academic or extracurricular achievements.")
    internships: List[Internship] = Field(description="Extracted internship history.")
    resume_text: str = Field(description="The raw text extracted from the student's resume.")
    resume_confidence: float = Field(description="Confidence score for resume parsing (0.0 to 1.0).")
    verified_sources: List[str] = Field(description="List of verified data source types.")
    github_analysis: GitHubAnalysis = Field(description="GitHub profiling placeholder data.")
    technical_score: int = Field(default=0, description="Readiness technical score (0-100).")
    project_score: int = Field(default=0, description="Readiness project score (0-100).")
    communication_score: int = Field(default=0, description="Readiness communication score (0-100).")
    interview_score: int = Field(default=0, description="Readiness interview score (0-100).")
    certification_score: int = Field(default=0, description="Readiness certification score (0-100).")
    placement_status: PlacementStatusEnum = Field(
        default=PlacementStatusEnum.UNPLACED,
        description="System placement status."
    )
    target_role_category: TargetRoleCategoryEnum = Field(
        default=TargetRoleCategoryEnum.SOFTWARE_ENGINEERING,
        description="Target role category."
    )
    profile_version: str = Field(default="1.0.0", description="Profile schema version.")
    extraction_method: Optional[str] = Field(default=None, description="The method of extraction used ('llm' or 'fallback').")
    overall_confidence: float = Field(description="Overall extraction confidence score (0.0 to 1.0).")
    explainability_section: ExplainabilitySection = Field(
        description="Evidence sentences backing every parsed field."
    )
    created_at: datetime = Field(description="Timestamp indicating profile creation.")
    updated_at: datetime = Field(description="Timestamp indicating last update.")
    github_url: Optional[str] = Field(default=None, description="Optional GitHub URL.")
    portfolio_url: Optional[str] = Field(default=None, description="Optional portfolio URL.")
    linkedin_url: Optional[str] = Field(default=None, description="Optional LinkedIn URL.")

    @field_validator("cgpa")
    @classmethod
    def validate_cgpa(cls, v: float) -> float:
        if not (0.0 <= v <= 10.0):
            raise ValueError("CGPA must be between 0.0 and 10.0.")
        return v

    @field_validator("resume_confidence", "overall_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence scores must be between 0.0 and 1.0.")
        return v

    @field_validator(
        "technical_score",
        "project_score",
        "communication_score",
        "interview_score",
        "certification_score",
    )
    @classmethod
    def validate_readiness_scores(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("Readiness scores must be between 0 and 100.")
        return v
