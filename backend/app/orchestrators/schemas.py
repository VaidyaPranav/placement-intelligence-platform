# Pydantic Schemas for Orchestrator Layer

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput
from backend.app.agents.ranking_agent.schemas import MatchResult
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport
from backend.app.agents.career_roadmap_agent.schemas import CareerRoadmap
from backend.app.agents.interview_agent.schemas import InterviewPreparationReport
from backend.app.config import PIPELINE_VERSION


class PipelineStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class PlacementAnalysisResult(BaseModel):
    student_profile: Optional[StudentProfile] = Field(None, description="The extracted student profile.")
    hiring_requirements: Optional[CompanyIntelligenceOutput] = Field(None, description="The extracted hiring requirements.")
    match_result: Optional[MatchResult] = Field(None, description="The ranking match result.")
    skill_gap_report: Optional[SkillGapReport] = Field(None, description="The skill gap report.")
    career_roadmap: Optional[CareerRoadmap] = Field(None, description="The generated career roadmap.")
    interview_report: Optional[InterviewPreparationReport] = Field(None, description="The interview prep report.")
    pipeline_status: PipelineStatusEnum = Field(description="Status of the pipeline execution.")
    errors: List[str] = Field(default_factory=list, description="List of error messages encountered.")
    execution_steps_completed: List[str] = Field(default_factory=list, description="List of successful step names.")
    execution_steps_failed: List[str] = Field(default_factory=list, description="List of failed or skipped step names.")
    total_execution_time_seconds: float = Field(description="Total execution time in seconds.")
    pipeline_version: str = Field(default=PIPELINE_VERSION, description="Version of the pipeline.")
