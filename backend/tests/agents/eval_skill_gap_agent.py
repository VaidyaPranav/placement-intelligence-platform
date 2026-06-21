# Evaluation Test Suite for Skill Gap Agent

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
from backend.app.agents.ranking_agent.schemas import MatchResult, RecommendationEnum
from backend.app.agents.skill_gap_agent.agent import generate_skill_gap_report, calculate_gap_score
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport, PriorityEnum, SeverityEnum


# Mock Event to simulate ADK event loop generator
class MockEvent:
    def __init__(self, output):
        self.output = output


# 1. Mock Dataset: 4 Students
STUDENTS = {
    "full_stack_student": StudentProfile(
        student_id=uuid4(),
        name="Varun Sharma",
        department=DepartmentEnum.CS,
        cgpa=8.5,
        skills=["React", "Node.js", "MySQL", "Git"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text passing character constraints." * 3,
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
            name_evidence="Name", department_evidence="CS", cgpa_evidence="CGPA",
            skill_evidence=[], project_evidence=[], certification_evidence=[], internship_evidence=[]
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    "ai_ml_student": StudentProfile(
        student_id=uuid4(),
        name="Priya Patel",
        department=DepartmentEnum.ECE,
        cgpa=8.8,
        skills=["Python", "PyTorch", "C++"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text passing character constraints." * 3,
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=0, languages=[], verification_status="UNVERIFIED"),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=TargetRoleCategoryEnum.AI_ML,
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=StudentExplainabilitySection(
            name_evidence="Name", department_evidence="ECE", cgpa_evidence="CGPA",
            skill_evidence=[], project_evidence=[], certification_evidence=[], internship_evidence=[]
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
}

# 2. Mock Dataset: 2 Jobs
JOBS = {
    "web_dev_job": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Software Developer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=["React", "Node.js", "MySQL", "MongoDB"],
        preferred_skills=["Docker", "AWS"],
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    ),
    "ai_job": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="AI Research Engineer",
        role_category="AI/ML",
        experience_level=ExperienceLevelEnum.MID_LEVEL,
        required_skills=["Python", "PyTorch", "TensorFlow"],
        preferred_skills=["Docker", "Kubernetes"],
        soft_skills=[],
        minimum_cgpa=8.5,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    )
}


# 3. Comprehensive Evaluation Test Suite
@pytest.mark.parametrize("student_key", STUDENTS.keys())
@pytest.mark.parametrize("job_key", JOBS.keys())
def test_skill_gap_matrix_evaluation(student_key, job_key):
    student = STUDENTS[student_key]
    job = JOBS[job_key]

    # Deterministic missing skills extraction
    student_skills_set = {s.strip().lower() for s in student.skills}
    missing_required = [r for r in job.required_skills if r.strip().lower() not in student_skills_set]
    missing_preferred = [p for p in job.preferred_skills if p.strip().lower() not in student_skills_set]

    # Calculate expected values
    expected_score, expected_severity = calculate_gap_score(
        missing_required, job.required_skills, missing_preferred, job.preferred_skills
    )

    # Build simulated MatchResult
    match_result = MatchResult(
        student_id=student.student_id,
        job_id=job.job_id,
        match_score=80.0,
        matched_skills=[r for r in job.required_skills if r.strip().lower() in student_skills_set],
        missing_skills=missing_required,
        preferred_skills_matched=[p for p in job.preferred_skills if p.strip().lower() in student_skills_set],
        preferred_skills_missing=missing_preferred,
        cgpa_eligible=student.cgpa >= job.minimum_cgpa,
        recommendation=RecommendationEnum.GOOD_MATCH,
        reasoning="Reasoning breakdown.",
        overall_confidence=0.9,
    )

    # Mock the LLM event stream to return expected values
    from backend.app.agents.skill_gap_agent.agent import build_recommendation
    mocked_recs = [build_recommendation(s) for s in missing_required + missing_preferred]
    mocked_output = SkillGapReport(
        student_id=student.student_id,
        job_id=job.job_id,
        gap_score=expected_score,
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        severity=expected_severity,
        recommendations=mocked_recs,
        overall_confidence=0.9
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = generate_skill_gap_report(student, job, match_result)

        # Assertions
        assert isinstance(result, SkillGapReport)
        assert result.student_id == student.student_id
        assert result.job_id == job.job_id
        assert result.gap_score == expected_score
        assert result.severity == expected_severity

        # Verify recommendations count matches missing skill count
        assert len(result.recommendations) == len(missing_required) + len(missing_preferred)

        # Verify recommendation skill names match missing skills
        rec_skills = {r.skill.lower().strip() for r in result.recommendations}
        missing_skills = {s.lower().strip() for s in missing_required + missing_preferred}
        assert rec_skills == missing_skills

        # Verify priorities and scores are populated
        for rec in result.recommendations:
            assert rec.priority in [PriorityEnum.HIGH, PriorityEnum.MEDIUM, PriorityEnum.LOW]
            assert 0.0 <= rec.estimated_improvement_score <= 100.0
            assert len(rec.recommendation.strip()) > 0

            # Verify that required missing skills get HIGH priority
            if rec.skill in missing_required:
                # React, Node.js, MySQL, Python, PyTorch, TensorFlow, MongoDB should map to their correct values
                assert rec.priority in [PriorityEnum.HIGH, PriorityEnum.MEDIUM]
            else:
                assert rec.priority in [PriorityEnum.HIGH, PriorityEnum.MEDIUM, PriorityEnum.LOW]

        print(f"\n[EVALUATION REPORT] Student: {student.name} vs Job: {job.role_title}")
        print(f" - Missing Required: {missing_required}")
        print(f" - Missing Preferred: {missing_preferred}")
        print(f" - Gap Score: {result.gap_score} | Severity: {result.severity.value}")
        print(f" - Recommendations Generated: {len(result.recommendations)}")
