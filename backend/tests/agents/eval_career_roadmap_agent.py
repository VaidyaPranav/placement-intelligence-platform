# Evaluation Test Suite for Career Roadmap Agent

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
from backend.app.agents.skill_gap_agent.schemas import (
    SkillGapReport,
    SkillRecommendation,
    PriorityEnum,
    SeverityEnum,
)
from backend.app.agents.career_roadmap_agent.agent import generate_career_roadmap
from backend.app.agents.career_roadmap_agent.schemas import CareerRoadmap, RoadmapWeek, RoadmapTask, DifficultyEnum


class MockEvent:
    def __init__(self, output):
        self.output = output


# Mock Student Profile
MOCK_STUDENT = StudentProfile(
    student_id=uuid4(),
    name="Evaluation Student",
    department=DepartmentEnum.CS,
    cgpa=9.0,
    skills=["Python"],
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


# Matrix inputs with varying severities and recommendations
GAP_REPORTS = [
    SkillGapReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=uuid4(),
        gap_score=15.0,
        missing_required_skills=["Git"],
        missing_preferred_skills=[],
        severity=SeverityEnum.LOW,
        recommendations=[
            SkillRecommendation(
                skill="Git",
                priority=PriorityEnum.LOW,
                recommendation="Learn Git.",
                estimated_improvement_score=5.0,
            )
        ],
        overall_confidence=0.9,
    ),
    SkillGapReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=uuid4(),
        gap_score=45.0,
        missing_required_skills=["Docker", "AWS"],
        missing_preferred_skills=[],
        severity=SeverityEnum.MEDIUM,
        recommendations=[
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
        ],
        overall_confidence=0.9,
    ),
    SkillGapReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=uuid4(),
        gap_score=75.0,
        missing_required_skills=["Docker", "React", "Node.js"],
        missing_preferred_skills=["AWS"],
        severity=SeverityEnum.HIGH,
        recommendations=[
            SkillRecommendation(skill="React", priority=PriorityEnum.HIGH, recommendation="Learn React.", estimated_improvement_score=10.0),
            SkillRecommendation(skill="Node.js", priority=PriorityEnum.HIGH, recommendation="Learn Node.js.", estimated_improvement_score=10.0),
            SkillRecommendation(skill="Docker", priority=PriorityEnum.HIGH, recommendation="Learn Docker.", estimated_improvement_score=12.0),
            SkillRecommendation(skill="AWS", priority=PriorityEnum.MEDIUM, recommendation="Learn AWS.", estimated_improvement_score=8.0),
        ],
        overall_confidence=0.9,
    ),
    SkillGapReport(
        student_id=MOCK_STUDENT.student_id,
        job_id=uuid4(),
        gap_score=90.0,
        missing_required_skills=["Docker", "React", "Node.js", "MySQL"],
        missing_preferred_skills=["AWS", "Git"],
        severity=SeverityEnum.CRITICAL,
        recommendations=[
            SkillRecommendation(skill="React", priority=PriorityEnum.HIGH, recommendation="Learn React.", estimated_improvement_score=10.0),
            SkillRecommendation(skill="Node.js", priority=PriorityEnum.HIGH, recommendation="Learn Node.js.", estimated_improvement_score=10.0),
            SkillRecommendation(skill="Docker", priority=PriorityEnum.HIGH, recommendation="Learn Docker.", estimated_improvement_score=12.0),
            SkillRecommendation(skill="MySQL", priority=PriorityEnum.HIGH, recommendation="Learn MySQL.", estimated_improvement_score=8.0),
            SkillRecommendation(skill="AWS", priority=PriorityEnum.MEDIUM, recommendation="Learn AWS.", estimated_improvement_score=8.0),
            SkillRecommendation(skill="Git", priority=PriorityEnum.LOW, recommendation="Learn Git.", estimated_improvement_score=5.0),
        ],
        overall_confidence=0.9,
    ),
]


@pytest.mark.parametrize("gap_report", GAP_REPORTS)
def test_career_roadmap_matrix_evaluation(gap_report):
    # Mock LLM response to match the target schema
    mock_weeks = []
    # Just construct dummy weeks/tasks for LLM mock.
    # The ADK wrapper post-processing must sort and clean them anyway.
    for i in range(1):
        mock_weeks.append(
            RoadmapWeek(
                week_number=i + 1,
                tasks=[
                    RoadmapTask(
                        week_number=i + 1,
                        skill=rec.skill,
                        title=f"Mock {rec.skill}",
                        description=f"Mock desc for {rec.skill}",
                        estimated_hours=6.0,
                        difficulty=DifficultyEnum.BEGINNER,
                    )
                    for rec in gap_report.recommendations
                ]
            )
        )

    mocked_output = CareerRoadmap(
        student_id=MOCK_STUDENT.student_id,
        total_weeks=len(mock_weeks),
        roadmap_weeks=mock_weeks,
        expected_match_score_improvement=0.0,
        overall_confidence=0.9,
        roadmap_version="1.0.0",
        generated_from_severity=gap_report.severity,
        roadmap_summary="Placeholder",
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = generate_career_roadmap(MOCK_STUDENT, gap_report)

        # Assertions
        assert isinstance(result, CareerRoadmap)
        assert result.student_id == MOCK_STUDENT.student_id
        assert result.roadmap_version == "1.0.0"
        assert result.generated_from_severity == gap_report.severity

        # Verify correct week counts based on severity mapping
        expected_weeks = {
            SeverityEnum.LOW: 1,
            SeverityEnum.MEDIUM: 2,
            SeverityEnum.HIGH: 3,
            SeverityEnum.CRITICAL: 4,
        }[gap_report.severity]
        assert result.total_weeks == expected_weeks
        assert len(result.roadmap_weeks) == expected_weeks

        # Verify expected improvement matches the sum of input recommendation scores
        expected_improvement = sum(r.estimated_improvement_score for r in gap_report.recommendations)
        assert result.expected_match_score_improvement == expected_improvement

        # Verify all skills from gap report are covered in tasks
        all_task_skills = {t.skill.lower().strip() for w in result.roadmap_weeks for t in w.tasks}
        expected_skills = {r.skill.lower().strip() for r in gap_report.recommendations}
        assert all_task_skills == expected_skills

        # Verify tasks are ordered by priority (HIGH tasks before MEDIUM and LOW tasks)
        # Flatten all tasks across all weeks
        flat_tasks = [t for w in result.roadmap_weeks for t in w.tasks]
        
        # Get priorities for skills
        priority_map = {r.skill.lower().strip(): r.priority for r in gap_report.recommendations}
        priority_levels = {PriorityEnum.HIGH: 0, PriorityEnum.MEDIUM: 1, PriorityEnum.LOW: 2}
        
        for idx in range(len(flat_tasks) - 1):
            curr_pri = priority_levels[priority_map[flat_tasks[idx].skill.lower().strip()]]
            next_pri = priority_levels[priority_map[flat_tasks[idx+1].skill.lower().strip()]]
            assert curr_pri <= next_pri

        # Verify summary content
        assert len(result.roadmap_summary.strip()) > 0
        assert f"{expected_improvement:.0f} points" in result.roadmap_summary or f"{expected_improvement:.1f} points" in result.roadmap_summary
        assert f"{expected_weeks}-week" in result.roadmap_summary
