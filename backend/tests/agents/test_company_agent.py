# Unit Tests for Company Intelligence Agent

import pytest
from uuid import uuid4
from unittest.mock import patch
from pydantic import ValidationError

from backend.app.agents.company_agent.agent import (
    extract_hiring_requirements,
    normalize_skill,
    get_role_category,
    fallback_regex_parse,
)
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput, ExperienceLevelEnum


# 1. Test Input Validation: Job Description Length
def test_short_job_description_validation():
    job_id = str(uuid4())
    short_text = "Short text."
    with pytest.raises(ValueError, match="Job description text must be at least 50 characters."):
        extract_hiring_requirements(job_id, short_text)


# 2. Test Input Validation: UUID Format
def test_invalid_uuid_validation():
    invalid_job_id = "invalid-uuid-string"
    long_text = "This is a long job description designed to pass the length check easily, but the UUID is invalid."
    with pytest.raises(ValueError, match="job_id must be a valid UUIDv4 string."):
        extract_hiring_requirements(invalid_job_id, long_text)


# 3. Test Skill Normalization Layer
@pytest.mark.parametrize(
    "input_skill,expected_skill",
    [
        ("ReactJS", "React"),
        ("React.js", "React"),
        ("NodeJS", "Node.js"),
        ("Node", "Node.js"),
        ("My SQL", "MySQL"),
        ("mysql", "MySQL"),
        ("AWS Cloud Practitioner", "AWS Cloud Practitioner"),
        ("aws certified cloud practitioner", "AWS Cloud Practitioner"),
        ("Python", "Python"),  # Unchanged
    ],
)
def test_skill_normalization(input_skill, expected_skill):
    assert normalize_skill(input_skill) == expected_skill


# 4. Test Role Taxonomy Mapping
@pytest.mark.parametrize(
    "role_title,expected_category",
    [
        ("Junior Cloud Backend Engineer", "Software Engineering"),
        ("Frontend Developer", "Software Engineering"),
        ("Data Analyst Intern", "Data & Analytics"),
        ("Machine Learning Engineer", "AI/ML"),
        ("AI Specialist", "AI/ML"),
        ("DevOps Architect", "Cloud & DevOps"),
        ("Systems Administrator", "Cloud & DevOps"),
        ("Unrecognized Random Title", "Software Engineering"),  # Default fallback
    ],
)
def test_role_taxonomy_mapping(role_title, expected_category):
    assert get_role_category(role_title) == expected_category


# 5. Test Fallback Regex Parser
def test_fallback_parser_extraction():
    job_id = str(uuid4())
    raw_text = """
    Title: Senior Python Developer
    We are seeking a developer with knowledge of Python, React and MySQL. 
    A minimum GPA of 8.0 is required for consideration. Intern candidate will not be considered.
    """
    result = fallback_regex_parse(job_id, raw_text, "Gemini API failed.")

    assert isinstance(result, CompanyIntelligenceOutput)
    assert result.job_id == pytest.approx(result.job_id)  # Compare UUID instances
    assert str(result.job_id) == job_id
    assert result.role_title == "Senior Python Developer"
    assert result.role_category == "Software Engineering"
    assert "Python" in result.required_skills or "Python" in result.preferred_skills
    assert result.minimum_cgpa == 8.0
    assert result.overall_confidence == 0.1  # Set to 0.1 for fallback
    assert result.explainability_section.role_evidence == "Parsed via regex title matcher."


# 6. Test 3-Attempt Recovery Loop (Triggering Fallback on Mock Error)
@patch("google.adk.runners.InMemoryRunner.run")
def test_repair_loop_calls_fallback_on_exception(mock_run):
    # Mock LLM API to raise validation/connection exception on every call
    mock_run.side_effect = Exception("Service unavailable or rate limited")
    
    job_id = str(uuid4())
    raw_text = """
    Title: Backend Developer
    Job description containing Python and Docker details. We need a minimum CGPA of 7.0 for juniors.
    """
    
    # Executing the extraction should catch the exception and return fallback
    result = extract_hiring_requirements(job_id, raw_text)
    
    assert mock_run.call_count == 3  # Verifies 3 attempts occurred before falling back
    assert isinstance(result, CompanyIntelligenceOutput)
    assert result.overall_confidence == 0.1  # Confirms fallback parser was used
