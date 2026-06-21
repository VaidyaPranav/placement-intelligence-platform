# Unit Tests for Student Intelligence Agent

import pytest
from uuid import uuid4
from unittest.mock import patch
from datetime import datetime

from backend.app.agents.student_agent.agent import (
    extract_student_profile,
    normalize_skill,
    adjust_project_complexity,
    map_department,
    predict_target_role_category,
    fallback_regex_parse,
)
from backend.app.agents.student_agent.schemas import (
    StudentProfile,
    Project,
    DepartmentEnum,
    TargetRoleCategoryEnum,
)


# 1. Test Input Validation: Resume Length
def test_short_resume_validation():
    student_id = str(uuid4())
    short_text = "Short text under 100 chars."
    with pytest.raises(ValueError, match="Resume text must be at least 100 characters."):
        extract_student_profile(student_id, short_text)


# 2. Test Input Validation: UUID Format
def test_invalid_uuid_validation():
    invalid_id = "invalid-uuid"
    long_text = "This is a long resume text designed to pass the length validation check easily. " * 3
    with pytest.raises(ValueError, match="student_id must be a valid UUIDv4 string."):
        extract_student_profile(invalid_id, long_text)


# 3. Test Skill Normalization
@pytest.mark.parametrize(
    "input_skill,expected_skill",
    [
        ("ReactJS", "React"),
        ("React.js", "React"),
        ("NodeJS", "Node.js"),
        ("Node", "Node.js"),
        ("My SQL", "MySQL"),
        ("mysql", "MySQL"),
        ("Tensor Flow", "TensorFlow"),
        ("tensorflow", "TensorFlow"),
        ("PowerBI", "Power BI"),
        ("power bi", "Power BI"),
        ("Python", "Python"),
    ],
)
def test_skill_normalization(input_skill, expected_skill):
    assert normalize_skill(input_skill) == expected_skill


# 4. Test Project Complexity Adjustment
@pytest.mark.parametrize(
    "title,score,expected_score",
    [
        ("A Simple CRUD Application", 9, 4),  # Clamp CRUD (3-4)
        ("React Web App Full Stack Project", 2, 6),  # Clamp Full Stack (5-7)
        ("AWS cloud deployment", 10, 8),  # Clamp Cloud (7-8)
        ("ResNet AI image classifier", 5, 9),  # Clamp AI/ML (8-10)
        ("Random Unrecognized Project", 7, 7),  # Keep unchanged
    ],
)
def test_project_complexity_adjustment(title, score, expected_score):
    assert adjust_project_complexity(title, score) == expected_score


# 5. Test Department Mapping
@pytest.mark.parametrize(
    "major_text,expected_dept",
    [
        ("B.Tech in Computer Science & Engineering", DepartmentEnum.CS),
        ("Master of Information Technology", DepartmentEnum.IT),
        ("Electronics and Communication Engineering", DepartmentEnum.ECE),
        ("Electrical Engineering department", DepartmentEnum.EE),
        ("Mechanical Engineering student", DepartmentEnum.ME),
        ("Some unrecognized major", DepartmentEnum.CS),  # Default
    ],
)
def test_department_mapping(major_text, expected_dept):
    assert map_department(major_text) == expected_dept


# 6. Test Target Role Category Prediction
def test_target_role_category_prediction():
    # AI/ML Prediction
    ai_role = predict_target_role_category(
        ["Python", "PyTorch"], [Project(title="AI Image Classifier", complexity_score=9)]
    )
    assert ai_role == TargetRoleCategoryEnum.AI_ML

    # Cloud & DevOps Prediction
    cloud_role = predict_target_role_category(
        ["AWS", "Docker"], [Project(title="Docker Setup", complexity_score=7)]
    )
    assert cloud_role == TargetRoleCategoryEnum.CLOUD_DEVOPS

    # Data & Analytics Prediction
    data_role = predict_target_role_category(
        ["SQL", "Power BI"], [Project(title="Sales Dashboard", complexity_score=4)]
    )
    assert data_role == TargetRoleCategoryEnum.DATA_ANALYTICS

    # Software Engineering Default Prediction
    se_role = predict_target_role_category(
        ["Java", "C++"], [Project(title="Algorithms", complexity_score=5)]
    )
    assert se_role == TargetRoleCategoryEnum.SOFTWARE_ENGINEERING


# 7. Test Fallback Regex Parser
def test_fallback_parser_extraction():
    student_id = str(uuid4())
    raw_text = """
    Amit Verma
    Email: amit.verma@example.com | GitHub: https://github.com/amitverma | LinkedIn: https://linkedin.com/in/amitverma
    B.Tech in Computer Science Engineering
    CGPA: 8.9 out of 10
    
    Skills: Python, ReactJS, NodeJS, My SQL, Docker
    
    Projects:
    - User Management CRUD: Built a simple CRUD app.
    - AI Chatbot: Built an NLP chatbot using PyTorch.
    
    Certifications:
    - React Developer Certificate from Meta
    
    Internships:
    - Web Developer Intern at RetailCorp (3 months)
    """

    profile = fallback_regex_parse(student_id, raw_text, "Gemini parsing failed.")

    assert isinstance(profile, StudentProfile)
    assert str(profile.student_id) == student_id
    assert profile.name == "Amit Verma"
    assert profile.department == DepartmentEnum.CS
    assert profile.cgpa == 8.9
    assert profile.github_url == "https://github.com/amitverma"
    assert profile.linkedin_url == "https://linkedin.com/in/amitverma"
    assert "React" in profile.skills
    assert "Node.js" in profile.skills
    assert "MySQL" in profile.skills
    assert profile.overall_confidence == 0.1
    assert profile.explainability_section.name_evidence == "Extracted via top line name parser."


# 8. Test 3-Attempt Recovery Loop
@patch("google.adk.runners.InMemoryRunner.run")
def test_repair_loop_calls_fallback_on_exception(mock_run):
    mock_run.side_effect = Exception("Service unavailable")
    
    student_id = str(uuid4())
    resume_text = """
    Rahul Sen
    Rahul is a computer science student with a CGPA of 9.2. He has experience with ReactJS and NodeJS.
    He completed a project called Cloud Setup. He did an internship at Google for 3 months.
    This resume has enough characters to pass the initial length check.
    """

    profile = extract_student_profile(student_id, resume_text)

    assert mock_run.call_count == 3
    assert isinstance(profile, StudentProfile)
    assert profile.overall_confidence == 0.1
