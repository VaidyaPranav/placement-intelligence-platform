# API Request/Response Schemas

from pydantic import BaseModel, Field
from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput
from backend.app.agents.ranking_agent.schemas import MatchResult
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport


class StudentAnalyzeRequest(BaseModel):
    student_id: str = Field(description="Unique UUIDv4 string representing the student.")
    resume_text: str = Field(description="Full raw text of the student's resume (at least 100 characters).")


class JobAnalyzeRequest(BaseModel):
    job_id: str = Field(description="Unique UUIDv4 string representing the job.")
    job_description: str = Field(description="Full raw text of the job description (at least 50 characters).")


class MatchRequest(BaseModel):
    student_profile: StudentProfile = Field(description="Validated StudentProfile object.")
    hiring_requirements: CompanyIntelligenceOutput = Field(description="Validated CompanyIntelligenceOutput object.")


class SkillGapRequest(BaseModel):
    student_profile: StudentProfile = Field(description="Validated StudentProfile object.")
    hiring_requirements: CompanyIntelligenceOutput = Field(description="Validated CompanyIntelligenceOutput object.")
    match_result: MatchResult = Field(description="Validated MatchResult object.")


class RoadmapRequest(BaseModel):
    student_profile: StudentProfile = Field(description="Validated StudentProfile object.")
    skill_gap_report: SkillGapReport = Field(description="Validated SkillGapReport object.")


class InterviewRequest(BaseModel):
    student_profile: StudentProfile = Field(description="Validated StudentProfile object.")
    hiring_requirements: CompanyIntelligenceOutput = Field(description="Validated CompanyIntelligenceOutput object.")
    match_result: MatchResult = Field(description="Validated MatchResult object.")
    skill_gap_report: SkillGapReport = Field(description="Validated SkillGapReport object.")


class FullAnalysisRequest(BaseModel):
    student_id: str = Field(description="Unique UUIDv4 string representing the student.")
    resume_text: str = Field(description="Full raw text of the student's resume.")
    job_id: str = Field(description="Unique UUIDv4 string representing the job.")
    job_description: str = Field(description="Full raw text of the job description.")


class AIStatusResponse(BaseModel):
    llm_enrichment_enabled: bool = Field(description="True if LLM enrichment is configured.")
    fallback_enabled: bool = Field(description="True if deterministic fallback is enabled.")
    gemini_api_configured: bool = Field(description="True if GOOGLE_API_KEY is present in environment.")
    status: str = Field(description="Real-time status: AI_ACTIVE, FALLBACK_MODE, or API_KEY_MISSING.")
