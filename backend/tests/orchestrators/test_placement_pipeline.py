# Unit Tests for Placement Pipeline Orchestrator

import pytest
from unittest.mock import patch
from uuid import uuid4
from datetime import datetime, timezone

from backend.app.orchestrators.placement_pipeline import run_full_placement_analysis
from backend.app.orchestrators.schemas import PipelineStatusEnum
from backend.app.agents.student_agent.schemas import (
    StudentProfile,
    DepartmentEnum,
    PlacementStatusEnum,
    TargetRoleCategoryEnum,
    GitHubAnalysis,
    ExplainabilitySection as StudentExplainabilitySection,
)
from backend.app.agents.company_agent.schemas import (
    CompanyIntelligenceOutput,
    ExperienceLevelEnum,
    ExplainabilitySection as JobExplainabilitySection,
)
from backend.app.agents.ranking_agent.schemas import MatchResult, RecommendationEnum
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport, SeverityEnum
from backend.app.agents.career_roadmap_agent.schemas import CareerRoadmap
from backend.app.agents.interview_agent.schemas import InterviewPreparationReport, DifficultyEnum


def get_mock_student_profile():
    return StudentProfile(
        student_id=uuid4(),
        name="Prep Student",
        department=DepartmentEnum.CS,
        cgpa=9.0,
        skills=["React", "Python"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume content that is long enough to satisfy constraints.",
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=2, languages=["Python"], verification_status="VERIFIED"),
        technical_score=80,
        project_score=85,
        communication_score=90,
        interview_score=80,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=TargetRoleCategoryEnum.SOFTWARE_ENGINEERING,
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=StudentExplainabilitySection(
            name_evidence="Ev",
            department_evidence="CS",
            cgpa_evidence="CGPA",
            skill_evidence=[],
            project_evidence=[],
            certification_evidence=[],
            internship_evidence=[],
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def get_mock_hiring_requirements():
    return CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Software Developer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=["React", "Docker"],
        preferred_skills=["AWS"],
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Ev", skill_evidence=[], cgpa_evidence="CGPA"),
    )


def get_mock_match_result():
    return MatchResult(
        student_id=uuid4(),
        job_id=uuid4(),
        match_score=80.0,
        recommendation=RecommendationEnum.GOOD_MATCH,
        matched_skills=["React"],
        missing_skills=["Docker"],
        preferred_skills_matched=[],
        preferred_skills_missing=["AWS"],
        cgpa_eligible=True,
        overall_confidence=0.9,
        reasoning="Good match.",
    )


def get_mock_skill_gap_report():
    return SkillGapReport(
        student_id=uuid4(),
        job_id=uuid4(),
        missing_required_skills=["Docker"],
        missing_preferred_skills=["AWS"],
        gap_score=50.0,
        severity=SeverityEnum.MEDIUM,
        recommendations=[],
        overall_confidence=0.9,
    )


def get_mock_career_roadmap():
    return CareerRoadmap(
        student_id=uuid4(),
        total_weeks=2,
        roadmap_weeks=[],
        expected_match_score_improvement=5.0,
        overall_confidence=0.9,
        roadmap_version="1.0.0",
        generated_from_severity=SeverityEnum.MEDIUM,
        roadmap_summary="Summary text."
    )


def get_mock_interview_report():
    return InterviewPreparationReport(
        student_id=uuid4(),
        job_id=uuid4(),
        role_title="Software Developer",
        technical_questions=[],
        behavioral_questions=[],
        weak_area_questions=[],
        strong_area_questions=[],
        focus_areas=["Docker"],
        overall_difficulty=DifficultyEnum.MEDIUM,
        estimated_interview_readiness_score=75.0,
        overall_confidence=0.9,
        interview_pack_version="1.0.0",
        generated_from_match_score=80.0,
        preparation_summary="Summary info."
    )


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_all_success(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Set up successful return values
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.return_value = get_mock_match_result()
    mock_gap.return_value = get_mock_skill_gap_report()
    mock_roadmap.return_value = get_mock_career_roadmap()
    mock_interview.return_value = get_mock_interview_report()

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content that is long enough.",
        job_id=str(uuid4()),
        job_description="Dummy job description content.",
    )

    assert result.pipeline_status == PipelineStatusEnum.SUCCESS
    assert len(result.errors) == 0
    assert len(result.execution_steps_completed) == 6
    assert len(result.execution_steps_failed) == 0
    assert result.student_profile is not None
    assert result.hiring_requirements is not None
    assert result.match_result is not None
    assert result.skill_gap_report is not None
    assert result.career_roadmap is not None
    assert result.interview_report is not None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_partial_success(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Student and Job agents succeed, Interview agent fails
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.return_value = get_mock_match_result()
    mock_gap.return_value = get_mock_skill_gap_report()
    mock_roadmap.return_value = get_mock_career_roadmap()
    mock_interview.side_effect = RuntimeError("Interview generation failed")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content that is long enough.",
        job_id=str(uuid4()),
        job_description="Dummy job description content.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert len(result.errors) == 1
    assert "Interview Agent failed: Interview generation failed" in result.errors
    assert "Interview Agent" in result.execution_steps_failed
    assert "Interview Agent" not in result.execution_steps_completed
    assert len(result.execution_steps_completed) == 5
    assert result.interview_report is None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_dependency_failure_propagation(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Student profile extracts successfully, but Company JD extraction fails.
    # Consequently, Ranking, Skill Gap, Roadmap, and Interview agents must be skipped.
    mock_student.return_value = get_mock_student_profile()
    mock_company.side_effect = RuntimeError("Job description parsing failed")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content that is long enough.",
        job_id=str(uuid4()),
        job_description="Dummy job description content.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Student Agent" in result.execution_steps_completed
    assert "Company Agent" in result.execution_steps_failed
    assert "Ranking Agent" in result.execution_steps_failed
    assert "Skill Gap Agent" in result.execution_steps_failed
    assert "Career Roadmap Agent" in result.execution_steps_failed
    assert "Interview Agent" in result.execution_steps_failed

    assert len(result.errors) == 5  # Company fails + 4 skips
    assert "Company Agent failed: Job description parsing failed" in result.errors
    assert "Ranking Agent skipped: missing required student profile or hiring requirements." in result.errors
    assert result.student_profile is not None
    assert result.hiring_requirements is None
    assert result.match_result is None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_company_agent_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Specific test validating what happens when Company Agent fails (Rank, Gap, Roadmap, Interview skipped)
    mock_student.return_value = get_mock_student_profile()
    mock_company.side_effect = ValueError("JD too short")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content that is long enough.",
        job_id=str(uuid4()),
        job_description="Too short",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Company Agent" in result.execution_steps_failed
    assert "Student Agent" in result.execution_steps_completed
    assert result.hiring_requirements is None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_student_agent_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Student profile fails. Rank, Gap, Roadmap, and Interview skipped. Company succeeds.
    mock_student.side_effect = ValueError("Resume text is empty")
    mock_company.return_value = get_mock_hiring_requirements()

    result = run_full_placement_analysis(
        student_id="invalid-uuid",
        resume_text="",
        job_id=str(uuid4()),
        job_description="Dummy job description content.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Student Agent" in result.execution_steps_failed
    assert "Company Agent" in result.execution_steps_completed
    assert result.student_profile is None
    assert result.hiring_requirements is not None
    assert result.match_result is None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_total_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    # Both initial extraction agents fail, leading to total failure
    mock_student.side_effect = RuntimeError("Student service crash")
    mock_company.side_effect = RuntimeError("Company service crash")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content that is long enough.",
        job_id=str(uuid4()),
        job_description="Dummy job description content.",
    )

    assert result.pipeline_status == PipelineStatusEnum.FAILED
    assert len(result.execution_steps_completed) == 0
    assert len(result.execution_steps_failed) == 6
    assert result.student_profile is None
    assert result.hiring_requirements is None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_ranking_agent_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.side_effect = RuntimeError("Ranking algorithm failed")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content.",
        job_id=str(uuid4()),
        job_description="Dummy job description.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Student Agent" in result.execution_steps_completed
    assert "Company Agent" in result.execution_steps_completed
    assert "Ranking Agent" in result.execution_steps_failed
    assert "Skill Gap Agent" in result.execution_steps_failed
    assert "Career Roadmap Agent" in result.execution_steps_failed
    assert "Interview Agent" in result.execution_steps_failed


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_skill_gap_agent_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.return_value = get_mock_match_result()
    mock_gap.side_effect = RuntimeError("Gap calculation failed")

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content.",
        job_id=str(uuid4()),
        job_description="Dummy job description.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Ranking Agent" in result.execution_steps_completed
    assert "Skill Gap Agent" in result.execution_steps_failed
    assert "Career Roadmap Agent" in result.execution_steps_failed
    assert "Interview Agent" in result.execution_steps_failed


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_roadmap_agent_failure(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.return_value = get_mock_match_result()
    mock_gap.return_value = get_mock_skill_gap_report()
    mock_roadmap.side_effect = RuntimeError("Roadmap builder crashed")
    mock_interview.return_value = get_mock_interview_report()

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content.",
        job_id=str(uuid4()),
        job_description="Dummy job description.",
    )

    assert result.pipeline_status == PipelineStatusEnum.PARTIAL_SUCCESS
    assert "Skill Gap Agent" in result.execution_steps_completed
    assert "Career Roadmap Agent" in result.execution_steps_failed
    assert "Interview Agent" in result.execution_steps_completed
    assert result.career_roadmap is None
    assert result.interview_report is not None


@patch("backend.app.orchestrators.placement_pipeline.extract_student_profile")
@patch("backend.app.orchestrators.placement_pipeline.extract_hiring_requirements")
@patch("backend.app.orchestrators.placement_pipeline.rank_student_against_job")
@patch("backend.app.orchestrators.placement_pipeline.generate_skill_gap_report")
@patch("backend.app.orchestrators.placement_pipeline.generate_career_roadmap")
@patch("backend.app.orchestrators.placement_pipeline.generate_interview_preparation_report")
def test_pipeline_time_measurement(
    mock_interview, mock_roadmap, mock_gap, mock_rank, mock_company, mock_student
):
    mock_student.return_value = get_mock_student_profile()
    mock_company.return_value = get_mock_hiring_requirements()
    mock_rank.return_value = get_mock_match_result()
    mock_gap.return_value = get_mock_skill_gap_report()
    mock_roadmap.return_value = get_mock_career_roadmap()
    mock_interview.return_value = get_mock_interview_report()

    result = run_full_placement_analysis(
        student_id=str(uuid4()),
        resume_text="Dummy student resume content.",
        job_id=str(uuid4()),
        job_description="Dummy job description.",
    )

    assert isinstance(result.total_execution_time_seconds, float)
    assert result.total_execution_time_seconds >= 0.0

