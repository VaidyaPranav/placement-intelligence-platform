# Unit Tests for Interview Agent

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
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport, PriorityEnum, SeverityEnum
from backend.app.agents.interview_agent.schemas import (
    InterviewPreparationReport,
    InterviewQuestion,
    DifficultyEnum,
)
from backend.app.agents.interview_agent.agent import (
    generate_interview_preparation_report,
    calculate_readiness_score,
    generate_focus_areas,
    build_question_for_skill,
)


# Helper to build mock student profile
def build_student(skills=None) -> StudentProfile:
    if skills is None:
        skills = ["React", "Python"]
    return StudentProfile(
        student_id=uuid4(),
        name="Prep Student",
        department=DepartmentEnum.CS,
        cgpa=9.0,
        skills=skills,
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy student resume for passing constraints testing." * 3,
        resume_confidence=0.95,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=1, languages=["Python"], verification_status="VERIFIED"),
        technical_score=85,
        project_score=80,
        communication_score=90,
        interview_score=85,
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


# Helper to build mock company requirements
def build_job(required=None, preferred=None) -> CompanyIntelligenceOutput:
    if required is None:
        required = ["React", "Docker"]
    if preferred is None:
        preferred = ["AWS"]
    return CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Software Developer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=required,
        preferred_skills=preferred,
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA"),
    )


# Helper to build mock match result
def build_match(student_id, job_id, rec=RecommendationEnum.GOOD_MATCH, missing_req=None, missing_pref=None) -> MatchResult:
    if missing_req is None:
        missing_req = ["Docker"]
    if missing_pref is None:
        missing_pref = ["AWS"]
    return MatchResult(
        student_id=student_id,
        job_id=job_id,
        match_score=75.0,
        matched_skills=["React"],
        missing_skills=missing_req,
        preferred_skills_matched=[],
        preferred_skills_missing=missing_pref,
        cgpa_eligible=True,
        recommendation=rec,
        reasoning="Reasoning breakdown.",
        overall_confidence=0.9,
    )


# Helper to build mock skill gap report
def build_gap(student_id) -> SkillGapReport:
    return SkillGapReport(
        student_id=student_id,
        job_id=uuid4(),
        gap_score=45.0,
        missing_required_skills=["Docker"],
        missing_preferred_skills=["AWS"],
        severity=SeverityEnum.MEDIUM,
        recommendations=[],
        overall_confidence=0.85,
    )


# 1. Test Schema Validation & Bounds
def test_question_schema_bounds():
    # Valid Question
    q = InterviewQuestion(
        question="What is React reconciliation?",
        skill="React",
        difficulty=DifficultyEnum.MEDIUM,
        expected_answer_keywords=["Virtual DOM", "Diffing"],
        evaluation_rubric=["Explains virtual DOM", "Explains reconciliation process"],
    )
    assert q.question == "What is React reconciliation?"

    # Empty expected_answer_keywords list
    with pytest.raises(ValidationError):
        InterviewQuestion(
            question="What is React reconciliation?",
            skill="React",
            difficulty=DifficultyEnum.MEDIUM,
            expected_answer_keywords=[],
            evaluation_rubric=["Explains virtual DOM"],
        )

    # Empty evaluation_rubric list
    with pytest.raises(ValidationError):
        InterviewQuestion(
            question="What is React reconciliation?",
            skill="React",
            difficulty=DifficultyEnum.MEDIUM,
            expected_answer_keywords=["Virtual DOM"],
            evaluation_rubric=[],
        )

    # Empty question string
    with pytest.raises(ValidationError):
        InterviewQuestion(
            question="",
            skill="React",
            difficulty=DifficultyEnum.MEDIUM,
            expected_answer_keywords=["Virtual DOM"],
            evaluation_rubric=["Explains virtual DOM"],
        )


# 2. Test Readiness Score Calculation
@pytest.mark.parametrize(
    "match_score, missing_req, missing_pref, matched_req, expected_score",
    [
        (80.0, ["Docker"], ["AWS"], ["React"], 76.0),  # 80.0 - 5.0 - 2.0 + 3.0 = 76.0
        (90.0, [], [], ["React", "Python"], 96.0),     # 90.0 - 0 - 0 + 6.0 = 96.0
        (20.0, ["Docker", "Kubernetes", "MySQL"], ["AWS", "Git"], [], 1.0),  # 20.0 - 15 - 4 = 1.0 (clamped or normal)
        (98.0, [], [], ["React"], 100.0),  # 98.0 + 3.0 = 101.0 -> Clamped to 100.0
    ],
)
def test_readiness_score_calculation(match_score, missing_req, missing_pref, matched_req, expected_score):
    score = calculate_readiness_score(match_score, missing_req, missing_pref, matched_req)
    assert score == expected_score


# 3. Test Difficulty Mapping
def test_difficulty_mapping():
    student = build_student()
    job = build_job()
    gap = build_gap(student.student_id)

    # STRONG_MATCH -> HARD
    match_res_strong = build_match(student.student_id, job.job_id, rec=RecommendationEnum.STRONG_MATCH)
    report_strong = generate_interview_preparation_report(student, job, match_res_strong, gap)
    assert report_strong.overall_difficulty == DifficultyEnum.HARD

    # GOOD_MATCH -> MEDIUM
    match_res_good = build_match(student.student_id, job.job_id, rec=RecommendationEnum.GOOD_MATCH)
    report_good = generate_interview_preparation_report(student, job, match_res_good, gap)
    assert report_good.overall_difficulty == DifficultyEnum.MEDIUM

    # WEAK_MATCH -> EASY
    match_res_weak = build_match(student.student_id, job.job_id, rec=RecommendationEnum.WEAK_MATCH)
    report_weak = generate_interview_preparation_report(student, job, match_res_weak, gap)
    assert report_weak.overall_difficulty == DifficultyEnum.EASY


# 4. Test Focus Areas Rules
def test_focus_areas_rules():
    # 3 missing required, 3 missing preferred
    # Expected focus areas:
    # 1. Include all missing required (Docker, Kubernetes, SQL)
    # 2. Include missing preferred up to total of 5 (AWS, Git)
    # 3. Alphabetically sorted: AWS, Docker, Git, Kubernetes, SQL
    missing_req = ["Docker", "Kubernetes", "SQL"]
    missing_pref = ["AWS", "Git", "MongoDB"]
    
    focus = generate_focus_areas(missing_req, missing_pref)
    assert len(focus) == 5
    assert focus == ["AWS", "Docker", "Git", "Kubernetes", "SQL"]


# 5. Test Question Generation & Rubric Population
def test_question_generation_and_rubrics():
    # React
    q_react = build_question_for_skill("React", DifficultyEnum.MEDIUM)
    assert q_react.skill == "React"
    assert q_react.question == "What is React reconciliation?"
    assert "Virtual DOM" in q_react.expected_answer_keywords
    assert len(q_react.evaluation_rubric) == 3
    assert "Explains virtual DOM" in q_react.evaluation_rubric

    # Docker
    q_docker = build_question_for_skill("Docker", DifficultyEnum.HARD)
    assert q_docker.skill == "Docker"
    assert q_docker.question == "What is the difference between a Docker image and a container?"
    assert len(q_docker.evaluation_rubric) == 3

    # Fallback
    q_fallback = build_question_for_skill("SomeCustomSkill", DifficultyEnum.EASY)
    assert q_fallback.skill == "SomeCustomSkill"
    assert q_fallback.question == "Explain the core concepts and best practices of using SomeCustomSkill in software development."
    assert "SomeCustomSkill" in q_fallback.expected_answer_keywords
    assert len(q_fallback.evaluation_rubric) == 3
    assert "Defines the technology" in q_fallback.evaluation_rubric


# 6. Test Serialization
def test_serialization():
    student = build_student()
    job = build_job()
    match_res = build_match(student.student_id, job.job_id)
    gap = build_gap(student.student_id)

    report = generate_interview_preparation_report(student, job, match_res, gap)
    dumped = report.model_dump_json()
    loaded = InterviewPreparationReport.model_validate_json(dumped)

    assert loaded.student_id == report.student_id
    assert loaded.interview_pack_version == "1.0.0"
    assert loaded.overall_difficulty == report.overall_difficulty
    assert len(loaded.technical_questions) == len(report.technical_questions)
    assert len(loaded.behavioral_questions) == 5
    assert loaded.preparation_summary == report.preparation_summary
