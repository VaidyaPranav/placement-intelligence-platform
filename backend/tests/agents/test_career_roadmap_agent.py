# Unit Tests for Career Roadmap Agent

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
from backend.app.agents.skill_gap_agent.schemas import (
    SkillGapReport,
    SkillRecommendation,
    PriorityEnum,
    SeverityEnum,
)
from backend.app.agents.career_roadmap_agent.schemas import (
    CareerRoadmap,
    RoadmapWeek,
    RoadmapTask,
    DifficultyEnum,
)
from backend.app.agents.career_roadmap_agent.agent import (
    generate_career_roadmap,
    generate_deterministic_roadmap,
    build_task_for_skill,
)


# Helper to build a student profile
def build_student_profile(skills=None) -> StudentProfile:
    if skills is None:
        skills = ["React"]
    return StudentProfile(
        student_id=uuid4(),
        name="Roadmap Student",
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


# Helper to build a skill gap report
def build_skill_gap_report(student_id, severity=SeverityEnum.MEDIUM, recommendations=None) -> SkillGapReport:
    if recommendations is None:
        recommendations = [
            SkillRecommendation(
                skill="Docker",
                priority=PriorityEnum.HIGH,
                recommendation="Learn Docker.",
                estimated_improvement_score=12.0,
            ),
            SkillRecommendation(
                skill="AWS",
                priority=PriorityEnum.MEDIUM,
                recommendation="Learn AWS.",
                estimated_improvement_score=8.0,
            ),
        ]
    return SkillGapReport(
        student_id=student_id,
        job_id=uuid4(),
        gap_score=45.0,
        missing_required_skills=["Docker"],
        missing_preferred_skills=["AWS"],
        severity=severity,
        recommendations=recommendations,
        overall_confidence=0.85,
    )


# 1. Test Schema Validation & Bounds
def test_roadmap_schema_bounds():
    # Valid Task
    task = RoadmapTask(
        week_number=1,
        skill="Docker",
        title="Containerization",
        description="Learn Docker files.",
        estimated_hours=6.0,
        difficulty=DifficultyEnum.BEGINNER,
    )
    assert task.week_number == 1

    # Invalid estimated_hours <= 0
    with pytest.raises(ValidationError):
        RoadmapTask(
            week_number=1,
            skill="Docker",
            title="Containerization",
            description="Learn Docker files.",
            estimated_hours=0.0,
            difficulty=DifficultyEnum.BEGINNER,
        )

    # Invalid empty title
    with pytest.raises(ValidationError):
        RoadmapTask(
            week_number=1,
            skill="Docker",
            title="",
            description="Learn Docker files.",
            estimated_hours=6.0,
            difficulty=DifficultyEnum.BEGINNER,
        )


# 2. Test Severity to Weeks Mapping
@pytest.mark.parametrize(
    "severity, expected_weeks",
    [
        (SeverityEnum.LOW, 1),
        (SeverityEnum.MEDIUM, 2),
        (SeverityEnum.HIGH, 3),
        (SeverityEnum.CRITICAL, 4),
    ],
)
def test_severity_to_weeks_mapping(severity, expected_weeks):
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id, severity=severity)
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    assert roadmap.total_weeks == expected_weeks
    assert len(roadmap.roadmap_weeks) == expected_weeks


# 3. Test Task Priority and Alphabetical Sorting
def test_task_sorting():
    # Mix priorities and alphabetical orders
    recs = [
        SkillRecommendation(skill="Git", priority=PriorityEnum.LOW, recommendation="Git description", estimated_improvement_score=5.0),
        SkillRecommendation(skill="React", priority=PriorityEnum.HIGH, recommendation="React description", estimated_improvement_score=10.0),
        SkillRecommendation(skill="Docker", priority=PriorityEnum.HIGH, recommendation="Docker description", estimated_improvement_score=12.0),
        SkillRecommendation(skill="AWS", priority=PriorityEnum.MEDIUM, recommendation="AWS description", estimated_improvement_score=8.0),
    ]
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id, severity=SeverityEnum.MEDIUM, recommendations=recs)
    
    # 2 weeks total for MEDIUM severity
    # Expected sorted order:
    # 1. Docker (HIGH, starts with D)
    # 2. React (HIGH, starts with R)
    # 3. AWS (MEDIUM)
    # 4. Git (LOW)
    # Distributed evenly: 4 tasks across 2 weeks -> 2 tasks per week
    # Week 1: Docker, React
    # Week 2: AWS, Git
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    
    assert len(roadmap.roadmap_weeks) == 2
    
    w1_skills = [t.skill for t in roadmap.roadmap_weeks[0].tasks]
    w2_skills = [t.skill for t in roadmap.roadmap_weeks[1].tasks]
    
    assert w1_skills == ["Docker", "React"]
    assert w2_skills == ["AWS", "Git"]


# 4. Test Expected Match Score Improvement Sum
def test_match_score_improvement_calculation():
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id)
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    # Docker (12.0) + AWS (8.0) = 20.0
    assert roadmap.expected_match_score_improvement == 20.0


# 5. Test Roadmap Version defaults to "1.0.0" and generated_from_severity is preserved
def test_roadmap_version_and_severity():
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id, severity=SeverityEnum.CRITICAL)
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    assert roadmap.roadmap_version == "1.0.0"
    assert roadmap.generated_from_severity == SeverityEnum.CRITICAL


# 6. Test Roadmap Summary Generation Content & Phrasing
def test_roadmap_summary_generation():
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id, severity=SeverityEnum.MEDIUM)
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    
    # Lead-in for MEDIUM: "This 2-week roadmap focuses on closing moderate skill gaps."
    # Detail sentence: "This 2-week roadmap covers 2 skills (Docker and AWS) and is expected to improve the student's match score by approximately 20 points."
    assert "moderate skill gaps" in roadmap.roadmap_summary
    assert "2-week roadmap covers 2 skills (Docker and AWS)" in roadmap.roadmap_summary
    assert "improve the student's match score by approximately 20 points" in roadmap.roadmap_summary


# 7. Test Serialization & Deserialization
def test_roadmap_serialization():
    student = build_student_profile()
    report = build_skill_gap_report(student.student_id)
    roadmap = generate_deterministic_roadmap(student.student_id, report)
    
    dumped = roadmap.model_dump_json()
    loaded = CareerRoadmap.model_validate_json(dumped)
    
    assert loaded.student_id == roadmap.student_id
    assert loaded.total_weeks == roadmap.total_weeks
    assert loaded.roadmap_summary == roadmap.roadmap_summary
    assert loaded.roadmap_version == "1.0.0"
    assert loaded.generated_from_severity == SeverityEnum.MEDIUM


# 8. Test Unknown Skill Handling
def test_unknown_skill_handling():
    rec = build_task_for_skill("UnknownSkillTag", 1)
    assert rec.skill == "UnknownSkillTag"
    assert rec.title == "Learn UnknownSkillTag Fundamentals"
    assert "UnknownSkillTag" in rec.description
    assert rec.estimated_hours == 6.0
    assert rec.difficulty == DifficultyEnum.BEGINNER
