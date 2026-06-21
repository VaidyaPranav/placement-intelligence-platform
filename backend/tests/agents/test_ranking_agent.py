# Unit Tests for Ranking Agent

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch

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
from backend.app.agents.ranking_agent.agent import (
    rank_student_against_job,
    calculate_match_details,
    get_recommendation,
    fallback_deterministic_rank,
)
from backend.app.agents.ranking_agent.schemas import MatchResult, RecommendationEnum


# 1. Test Helpers to generate Mock Inputs
def build_student_profile(cgpa=8.5, skills=None) -> StudentProfile:
    if skills is None:
        skills = ["React", "Node.js", "MySQL"]
    return StudentProfile(
        student_id=uuid4(),
        name="Test Student",
        department=DepartmentEnum.CS,
        cgpa=cgpa,
        skills=skills,
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="This is a dummy resume text with a length long enough to pass validation rules. " * 3,
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=0, languages=[], verification_status="UNVERIFIED"),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=TargetRoleCategoryEnum.SOFTWARE_ENGINEERING,
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=StudentExplainabilitySection(
            name_evidence="Name",
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


def build_job_requirements(minimum_cgpa=8.0, required_skills=None, preferred_skills=None) -> CompanyIntelligenceOutput:
    if required_skills is None:
        required_skills = ["React", "Node.js", "MySQL", "Git"]
    if preferred_skills is None:
        preferred_skills = ["Docker", "AWS"]
    return CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Software Engineer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        soft_skills=[],
        minimum_cgpa=minimum_cgpa,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(
            role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA"
        ),
    )


# 2. Test Scoring Engine: Perfect Match (100%)
def test_scoring_perfect_match():
    score, m_req, ms_req, m_pref, ms_pref, cgpa_el = calculate_match_details(
        student_skills=["React", "Node.js", "MySQL", "Git", "Docker", "AWS"],
        required_skills=["React", "Node.js", "MySQL", "Git"],
        preferred_skills=["Docker", "AWS"],
        student_cgpa=9.0,
        minimum_cgpa=8.0,
    )
    assert score == 100.0
    assert len(m_req) == 4
    assert len(ms_req) == 0
    assert len(m_pref) == 2
    assert len(ms_pref) == 0
    assert cgpa_el is True


# 3. Test Scoring Engine: Partial Match (72.5%)
def test_scoring_partial_match():
    score, m_req, ms_req, m_pref, ms_pref, cgpa_el = calculate_match_details(
        student_skills=["React", "Node.js", "MySQL", "Docker"],
        required_skills=["React", "Node.js", "MySQL", "Git"],
        preferred_skills=["Docker", "AWS"],
        student_cgpa=8.5,
        minimum_cgpa=8.0,
    )
    # Required skills = 3/4 (75% match, 75 * 0.70 = 52.5)
    # Preferred skills = 1/2 (50% match, 50 * 0.20 = 10.0)
    # CGPA = True (100% match, 100 * 0.10 = 10.0)
    # Final match score = 52.5 + 10.0 + 10.0 = 72.5
    assert score == 72.5
    assert len(ms_req) == 1
    assert len(ms_pref) == 1
    assert cgpa_el is True


# 4. Test Recommendation Mappings
@pytest.mark.parametrize(
    "score,cgpa_el,expected_rec",
    [
        (95.0, True, RecommendationEnum.STRONG_MATCH),
        (85.0, True, RecommendationEnum.GOOD_MATCH),
        (70.0, True, RecommendationEnum.PARTIAL_MATCH),
        (50.0, True, RecommendationEnum.WEAK_MATCH),
        (30.0, True, RecommendationEnum.NOT_ELIGIBLE),
        (95.0, False, RecommendationEnum.NOT_ELIGIBLE),  # CGPA failure override
    ],
)
def test_recommendation_mapping(score, cgpa_el, expected_rec):
    assert get_recommendation(score, cgpa_el) == expected_rec


# 5. Test input validations
def test_invalid_input_types():
    with pytest.raises(ValueError, match="student_profile must be a valid StudentProfile instance."):
        rank_student_against_job("not_a_student", build_job_requirements())

    with pytest.raises(ValueError, match="hiring_requirements must be a valid CompanyIntelligenceOutput instance."):
        rank_student_against_job(build_student_profile(), "not_a_job")


# 6. Test Fallback Deterministic Local Match Result
def test_fallback_deterministic_result():
    student = build_student_profile(cgpa=7.5, skills=["React"])
    job = build_job_requirements(minimum_cgpa=8.0, required_skills=["React", "Node.js"])

    res = fallback_deterministic_rank(
        student.student_id,
        job.job_id,
        student.skills,
        job.required_skills,
        job.preferred_skills,
        student.cgpa,
        job.minimum_cgpa,
        "Mock Trigger Error",
    )

    assert isinstance(res, MatchResult)
    assert res.cgpa_eligible is False
    assert res.recommendation == RecommendationEnum.NOT_ELIGIBLE
    assert res.overall_confidence == 0.1
    assert "Mock Trigger Error" in res.reasoning


# 7. Test Fallback on ADK Failure
@patch("google.adk.runners.InMemoryRunner.run")
def test_repair_loop_calls_fallback_on_exception(mock_run):
    mock_run.side_effect = Exception("Gemini Connection Timeout")
    
    student = build_student_profile()
    job = build_job_requirements()

    # Enable LLM enrichment for this test to trigger the ADK runner
    import backend.app.agents.ranking_agent.agent as agent_mod
    with patch.object(agent_mod, "USE_LLM_ENRICHMENT", True):
        res = rank_student_against_job(student, job)

    assert mock_run.call_count == 1  # Fast-fallback: no excessive retries
    assert isinstance(res, MatchResult)
    assert res.overall_confidence == 0.1


# 8. Test Score Breakdown Fields Population
def test_score_breakdown_population():
    student = build_student_profile(cgpa=8.5, skills=["React", "Git"])
    job = build_job_requirements(minimum_cgpa=8.0, required_skills=["React", "Node.js"], preferred_skills=["Git", "Docker"])

    res = fallback_deterministic_rank(
        student.student_id,
        job.job_id,
        student.skills,
        job.required_skills,
        job.preferred_skills,
        student.cgpa,
        job.minimum_cgpa,
        "Testing Breakdown",
    )

    assert res.required_skill_score == 50.0  # 1 out of 2 matched
    assert res.preferred_skill_score == 50.0  # 1 out of 2 matched
    assert res.cgpa_score == 100.0  # 8.5 >= 8.0


