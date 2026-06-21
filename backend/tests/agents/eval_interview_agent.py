# Evaluation Test Suite for Interview Agent

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
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport, SeverityEnum
from backend.app.agents.interview_agent.agent import generate_interview_preparation_report
from backend.app.agents.interview_agent.schemas import (
    InterviewPreparationReport,
    InterviewQuestion,
    DifficultyEnum,
)


class MockEvent:
    def __init__(self, output):
        self.output = output


# Mock Student Profile
MOCK_STUDENT = StudentProfile(
    student_id=uuid4(),
    name="Eval Candidate",
    department=DepartmentEnum.CS,
    cgpa=8.8,
    skills=["Python", "SQL", "Git"],
    projects=[],
    certifications=[],
    achievements=[],
    internships=[],
    resume_text="Evaluation student resume text passing constraints." * 3,
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
)

# Mock Jobs
JOBS = [
    CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Backend Engineer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=["Python", "Docker"],
        preferred_skills=["AWS", "Git"],
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    ),
    CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Full Stack Developer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.MID_LEVEL,
        required_skills=["React", "Node.js", "SQL"],
        preferred_skills=["Git", "Docker"],
        soft_skills=[],
        minimum_cgpa=8.5,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    )
]


@pytest.mark.parametrize("job", JOBS)
def test_interview_prep_matrix_evaluation(job):
    student_skills_set = {s.strip().lower() for s in MOCK_STUDENT.skills}
    missing_required = [r for r in job.required_skills if r.strip().lower() not in student_skills_set]
    missing_preferred = [p for p in job.preferred_skills if p.strip().lower() not in student_skills_set]
    
    matched_required = [r for r in job.required_skills if r.strip().lower() in student_skills_set]
    matched_preferred = [p for p in job.preferred_skills if p.strip().lower() in student_skills_set]

    # Mock MatchResult
    match_res = MatchResult(
        student_id=MOCK_STUDENT.student_id,
        job_id=job.job_id,
        match_score=80.0,
        matched_skills=matched_required,
        missing_skills=missing_required,
        preferred_skills_matched=matched_preferred,
        preferred_skills_missing=missing_preferred,
        cgpa_eligible=True,
        recommendation=RecommendationEnum.GOOD_MATCH,
        reasoning="Dummy reasoning",
        overall_confidence=0.9,
    )

    # Mock SkillGapReport
    gap_report = SkillGapReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=job.job_id,
        gap_score=40.0,
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        severity=SeverityEnum.MEDIUM,
        recommendations=[],
        overall_confidence=0.9,
    )

    # Mock LLM Response matching target schema
    mock_tech_qs = []
    # Fill in dummy parsed questions to test ADK wrapper post-processing/enrichment
    for s in missing_required + matched_required + missing_preferred + matched_preferred:
        mock_tech_qs.append(
            InterviewQuestion(
                question=f"Mock question for {s}",
                skill=s,
                difficulty=DifficultyEnum.MEDIUM,
                expected_answer_keywords=["mock"],
                evaluation_rubric=["mock rubric item"],
            )
        )

    mocked_output = InterviewPreparationReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=job.job_id,
        role_title=job.role_title,
        technical_questions=mock_tech_qs,
        behavioral_questions=[],
        weak_area_questions=[],
        strong_area_questions=[],
        focus_areas=[],
        overall_difficulty=DifficultyEnum.MEDIUM,
        estimated_interview_readiness_score=80.0,
        overall_confidence=0.9,
        interview_pack_version="1.0.0",
        generated_from_match_score=80.0,
        preparation_summary="Placeholder summary",
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = generate_interview_preparation_report(MOCK_STUDENT, job, match_res, gap_report)

        # Assertions
        assert isinstance(result, InterviewPreparationReport)
        assert result.student_id == MOCK_STUDENT.student_id
        assert result.job_id == job.job_id
        assert result.role_title == job.role_title
        assert result.interview_pack_version == "1.0.0"

        # Verify behavioral questions count = 5
        assert len(result.behavioral_questions) == 5

        # Verify readiness score populated
        assert 0.0 <= result.estimated_interview_readiness_score <= 100.0

        # Verify preparation summary populated
        assert len(result.preparation_summary.strip()) > 0

        # Verify every technical question contains rubric and keywords
        for q in result.technical_questions + result.weak_area_questions + result.strong_area_questions:
            assert len(q.evaluation_rubric) >= 1
            assert len(q.expected_answer_keywords) >= 1
            assert len(q.question.strip()) > 0
            assert len(q.skill.strip()) > 0

        # Verify focus_areas align with missing skills
        expected_focus = sorted(list(set(missing_required + (missing_preferred if len(missing_required) < 5 else []))))[:5]
        expected_focus.sort()
        assert result.focus_areas == expected_focus

        # Verify weak area questions cover missing required and preferred skills
        weak_skills_in_questions = {q.skill.lower().strip() for q in result.weak_area_questions}
        expected_weak_skills = {s.lower().strip() for s in missing_required + missing_preferred}
        assert weak_skills_in_questions == expected_weak_skills

        # Verify strong area questions cover matched required and preferred skills
        strong_skills_in_questions = {q.skill.lower().strip() for q in result.strong_area_questions}
        expected_strong_skills = {s.lower().strip() for s in matched_required + matched_preferred}
        assert strong_skills_in_questions == expected_strong_skills
