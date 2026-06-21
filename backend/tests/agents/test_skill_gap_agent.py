# Unit Tests for Skill Gap Agent

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

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
from backend.app.agents.skill_gap_agent.agent import (
    generate_skill_gap_report,
    calculate_gap_score,
    build_recommendation,
)
from backend.app.agents.skill_gap_agent.schemas import (
    SkillGapReport,
    SkillRecommendation,
    PriorityEnum,
    SeverityEnum,
)


# 1. Test Helpers to generate Mock Inputs
def build_student_profile(skills=None) -> StudentProfile:
    if skills is None:
        skills = ["React", "Node.js"]
    return StudentProfile(
        student_id=uuid4(),
        name="Test Student",
        department=DepartmentEnum.CS,
        cgpa=8.5,
        skills=skills,
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text for student passing character constraints." * 3,
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


def build_job_requirements(required_skills=None, preferred_skills=None) -> CompanyIntelligenceOutput:
    if required_skills is None:
        required_skills = ["React", "Node.js", "MySQL"]
    if preferred_skills is None:
        preferred_skills = ["Docker"]
    return CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Software Engineer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(
            role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA"
        ),
    )


def build_match_result(student_id, job_id, missing_skills=None, preferred_missing=None) -> MatchResult:
    if missing_skills is None:
        missing_skills = ["MySQL"]
    if preferred_missing is None:
        preferred_missing = ["Docker"]
    return MatchResult(
        student_id=student_id,
        job_id=job_id,
        match_score=75.0,
        matched_skills=["React", "Node.js"],
        missing_skills=missing_skills,
        preferred_skills_matched=[],
        preferred_skills_missing=preferred_missing,
        cgpa_eligible=True,
        recommendation=RecommendationEnum.GOOD_MATCH,
        reasoning="Reasoning breakdown.",
        overall_confidence=0.9,
    )


# 2. Test SkillRecommendation Schema Validation & Bounds
def test_skill_recommendation_bounds():
    # Valid
    rec = SkillRecommendation(
        skill="Docker",
        priority=PriorityEnum.HIGH,
        recommendation="Learn containerization.",
        estimated_improvement_score=12.0,
    )
    assert rec.skill == "Docker"
    assert rec.estimated_improvement_score == 12.0

    # Invalid empty skill
    with pytest.raises(ValidationError):
        SkillRecommendation(
            skill="",
            priority=PriorityEnum.HIGH,
            recommendation="Learn containerization.",
            estimated_improvement_score=12.0,
        )

    # Invalid empty recommendation
    with pytest.raises(ValidationError):
        SkillRecommendation(
            skill="Docker",
            priority=PriorityEnum.HIGH,
            recommendation=" ",
            estimated_improvement_score=12.0,
        )

    # Invalid improvement score bounds (> 100)
    with pytest.raises(ValidationError):
        SkillRecommendation(
            skill="Docker",
            priority=PriorityEnum.HIGH,
            recommendation="Learn containerization.",
            estimated_improvement_score=105.0,
        )

    # Invalid improvement score bounds (< 0)
    with pytest.raises(ValidationError):
        SkillRecommendation(
            skill="Docker",
            priority=PriorityEnum.HIGH,
            recommendation="Learn containerization.",
            estimated_improvement_score=-5.0,
        )


# 3. Test Severity Mapping & Gap Score Calculations
@pytest.mark.parametrize(
    "missing_req, total_req, missing_pref, total_pref, expected_score, expected_severity",
    [
        # Perfect Match: 0% gap -> LOW
        ([], ["React"], [], ["Docker"], 0.0, SeverityEnum.LOW),
        # 1/3 required missing (33.3% * 70 = 23.33) -> MEDIUM
        (["MySQL"], ["React", "Node.js", "MySQL"], [], ["Docker"], 23.33, SeverityEnum.MEDIUM),
        # 1/2 required missing (50% * 70 = 35.0) + 1/1 preferred missing (100% * 30 = 30.0) -> 65.0 -> HIGH
        (["MySQL"], ["React", "MySQL"], ["Docker"], ["Docker"], 65.0, SeverityEnum.HIGH),
        # All required missing (100% * 70 = 70.0) + All preferred missing (100% * 30 = 30.0) -> 100.0 -> CRITICAL
        (["React", "MySQL"], ["React", "MySQL"], ["Docker"], ["Docker"], 100.0, SeverityEnum.CRITICAL),
    ],
)
def test_gap_score_and_severity_calculations(
    missing_req, total_req, missing_pref, total_pref, expected_score, expected_severity
):
    score, severity = calculate_gap_score(missing_req, total_req, missing_pref, total_pref)
    assert score == expected_score
    assert severity == expected_severity


# 4. Test Recommendation Generation from Dictionary
def test_recommendation_library_generation():
    # React lookup
    rec_react = build_recommendation("React")
    assert rec_react.skill == "React"
    assert rec_react.priority == PriorityEnum.HIGH
    assert rec_react.estimated_improvement_score == 10.0
    assert "routing" in rec_react.recommendation

    # AWS lookup
    rec_aws = build_recommendation("AWS")
    assert rec_aws.skill == "AWS"
    assert rec_aws.priority == PriorityEnum.MEDIUM
    assert rec_aws.estimated_improvement_score == 8.0


# 5. Test Unknown Skill Fallback Generation
def test_unknown_skill_fallback():
    rec_unknown = build_recommendation("SomeWeirdSkill")
    assert rec_unknown.skill == "SomeWeirdSkill"
    assert rec_unknown.priority == PriorityEnum.LOW
    assert rec_unknown.estimated_improvement_score == 5.0
    assert "fundamentals of SomeWeirdSkill" in rec_unknown.recommendation


# 6. Test SkillGapReport Serialization
def test_report_serialization():
    student = build_student_profile()
    job = build_job_requirements()
    match_res = build_match_result(student.student_id, job.job_id)

    report = generate_skill_gap_report(student, job, match_res)

    assert isinstance(report, SkillGapReport)
    assert report.student_id == student.student_id
    assert report.job_id == job.job_id
    assert len(report.recommendations) == 2
    assert report.overall_confidence == 0.1

    # Check Pydantic JSON Dump
    dumped_json = report.model_dump_json()
    assert "estimated_improvement_score" in dumped_json
    assert "priority" in dumped_json
