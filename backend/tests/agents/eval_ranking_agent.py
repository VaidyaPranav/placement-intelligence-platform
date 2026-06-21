# Evaluation Test Suite for Ranking Agent

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
from backend.app.agents.ranking_agent.agent import rank_student_against_job, calculate_match_details, get_recommendation
from backend.app.agents.ranking_agent.schemas import MatchResult, RecommendationEnum


# Mock Event to simulate ADK event loop generator
class MockEvent:
    def __init__(self, output):
        self.output = output


# 1. Mock Students Dataset
STUDENTS = {
    "student_1": StudentProfile(
        student_id=uuid4(),
        name="Varun FullStack",
        department=DepartmentEnum.CS,
        cgpa=9.2,
        skills=["React", "Node.js", "MySQL", "Git", "Docker", "AWS", "Python", "PyTorch"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text for student 1 passing character constraints." * 3,
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
    "student_2": StudentProfile(
        student_id=uuid4(),
        name="Aditya CloudDevOps",
        department=DepartmentEnum.IT,
        cgpa=8.1,
        skills=["AWS", "Docker", "Terraform", "Kubernetes", "Linux", "Bash", "Python"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text for student 2 passing character constraints." * 3,
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=0, languages=[], verification_status="UNVERIFIED"),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=TargetRoleCategoryEnum.CLOUD_DEVOPS,
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=StudentExplainabilitySection(
            name_evidence="Name", department_evidence="IT", cgpa_evidence="CGPA",
            skill_evidence=[], project_evidence=[], certification_evidence=[], internship_evidence=[]
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    "student_3": StudentProfile(
        student_id=uuid4(),
        name="Priya AIML",
        department=DepartmentEnum.ECE,
        cgpa=8.6,
        skills=["Python", "PyTorch", "TensorFlow", "Computer Vision", "OpenCV", "NumPy", "C++"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text for student 3 passing character constraints." * 3,
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
    ),
    "student_4": StudentProfile(
        student_id=uuid4(),
        name="Kunal DataAnalyst",
        department=DepartmentEnum.IT,
        cgpa=7.4,
        skills=["SQL", "Tableau", "Power BI", "Excel", "Pandas", "Matplotlib", "Python"],
        projects=[],
        certifications=[],
        achievements=[],
        internships=[],
        resume_text="Dummy resume text for student 4 passing character constraints." * 3,
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=0, languages=[], verification_status="UNVERIFIED"),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=TargetRoleCategoryEnum.DATA_ANALYTICS,
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=StudentExplainabilitySection(
            name_evidence="Name", department_evidence="IT", cgpa_evidence="CGPA",
            skill_evidence=[], project_evidence=[], certification_evidence=[], internship_evidence=[]
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
}


# 2. Mock Jobs Dataset
JOBS = {
    "job_1_full_stack": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Full Stack Software Engineer",
        role_category="Software Engineering",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=["React", "Node.js", "MySQL"],
        preferred_skills=["Docker", "Git"],
        soft_skills=[],
        minimum_cgpa=8.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    ),
    "job_2_ai_engineer": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Machine Learning Engineer",
        role_category="AI/ML",
        experience_level=ExperienceLevelEnum.MID_LEVEL,
        required_skills=["Python", "PyTorch", "TensorFlow"],
        preferred_skills=["Docker", "C++"],
        soft_skills=[],
        minimum_cgpa=8.5,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    ),
    "job_3_data_analyst": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Business Intelligence Analyst",
        role_category="Data & Analytics",
        experience_level=ExperienceLevelEnum.ENTRY_LEVEL,
        required_skills=["SQL", "Tableau", "Excel"],
        preferred_skills=["Python"],
        soft_skills=[],
        minimum_cgpa=7.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    ),
    "job_4_cloud_devops": CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title="Cloud Infrastructure Architect",
        role_category="Cloud & DevOps",
        experience_level=ExperienceLevelEnum.SENIOR,
        required_skills=["AWS", "Docker"],
        preferred_skills=["Linux", "Bash"],
        soft_skills=[],
        minimum_cgpa=9.0,
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=0.9,
        cgpa_confidence=0.9,
        explainability_section=JobExplainabilitySection(role_evidence="Role", skill_evidence=[], cgpa_evidence="CGPA")
    )
}


# 3. Comprehensive Matrix Evaluation Test (16 Scenarios)
@pytest.mark.parametrize("student_key", STUDENTS.keys())
@pytest.mark.parametrize("job_key", JOBS.keys())
def test_ranking_matrix_accuracy(student_key, job_key):
    student = STUDENTS[student_key]
    job = JOBS[job_key]

    # Calculate expected values deterministically
    expected_score, expected_m_req, expected_ms_req, expected_m_pref, expected_ms_pref, expected_cgpa_el = calculate_match_details(
        student.skills,
        job.required_skills,
        job.preferred_skills,
        student.cgpa,
        job.minimum_cgpa
    )
    expected_rec = get_recommendation(expected_score, expected_cgpa_el)

    # Build simulated ADK output matching expected fields
    mocked_output = MatchResult(
        student_id=student.student_id,
        job_id=job.job_id,
        match_score=expected_score,
        matched_skills=expected_m_req,
        missing_skills=expected_ms_req,
        preferred_skills_matched=expected_m_pref,
        preferred_skills_missing=expected_ms_pref,
        cgpa_eligible=expected_cgpa_el,
        recommendation=expected_rec,
        reasoning="Simulated ADK explainability reasoning.",
        overall_confidence=0.9
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = rank_student_against_job(student, job)

        # Assert full MatchResult correctness
        assert isinstance(result, MatchResult)
        assert result.student_id == student.student_id
        assert result.job_id == job.job_id
        assert result.cgpa_eligible == expected_cgpa_el
        assert result.match_score == expected_score
        assert result.recommendation == expected_rec

        # Assert skills mapping accuracy
        assert sorted(result.matched_skills) == sorted(expected_m_req)
        assert sorted(result.missing_skills) == sorted(expected_ms_req)
        assert sorted(result.preferred_skills_matched) == sorted(expected_m_pref)
        assert sorted(result.preferred_skills_missing) == sorted(expected_ms_pref)

        # Output diagnostic logs
        print(f"\n[RANK EVALUATION REPORT] {student.name} vs {job.role_title}")
        print(f" - Mapped Match Score: {result.match_score:.2f}")
        print(f" - CGPA Eligible: {result.cgpa_eligible}")
        print(f" - Recommendation Result: {result.recommendation.value}")
