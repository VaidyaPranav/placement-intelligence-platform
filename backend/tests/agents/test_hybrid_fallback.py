# Integration and Unit Tests for Hybrid AI + Deterministic Fallback Architecture

import pytest
import concurrent.futures
from uuid import uuid4
from unittest.mock import patch, MagicMock
from google.genai.errors import ClientError

from backend.app.agents.student_agent.agent import extract_student_profile, StudentProfile
from backend.app.agents.company_agent.agent import extract_hiring_requirements, CompanyIntelligenceOutput
from backend.app.orchestrators.placement_pipeline import run_full_placement_analysis
from backend.app.orchestrators.schemas import PlacementAnalysisResult, PipelineStatusEnum

class MockEvent:
    def __init__(self, output=None, content=None):
        self.output = output
        self.content = content


# 1. Test Gemini Success Path
@patch("google.adk.runners.InMemoryRunner.run")
def test_gemini_success_path(mock_run):
    student_id = str(uuid4())
    resume_text = "My name is John Doe. I am a CS student. My CGPA is 9.5. I know Python, React, and Git. " * 3

    # Create a mock StudentProfile to be returned on success
    mock_profile = StudentProfile.model_validate({
        "student_id": student_id,
        "name": "John Doe",
        "department": "CS",
        "cgpa": 9.5,
        "skills": ["Python", "React"],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "internships": [],
        "resume_text": resume_text,
        "resume_confidence": 0.9,
        "verified_sources": ["RESUME_PDF"],
        "github_analysis": {
            "repo_count": 0,
            "languages": [],
            "verification_status": "UNVERIFIED"
        },
        "overall_confidence": 0.95,
        "explainability_section": {
            "name_evidence": "John Doe",
            "department_evidence": "CS",
            "cgpa_evidence": "9.5",
            "skill_evidence": [],
            "project_evidence": [],
            "certification_evidence": [],
            "internship_evidence": []
        },
        "created_at": "2026-06-21T12:00:00Z",
        "updated_at": "2026-06-21T12:00:00Z"
    })

    mock_run.return_value = [MockEvent(output=mock_profile)]

    profile = extract_student_profile(student_id, resume_text)

    assert isinstance(profile, StudentProfile)
    assert profile.extraction_method == "llm"
    assert profile.overall_confidence == 0.95
    assert profile.name == "John Doe"


# 2. Test Missing API Key Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_missing_api_key_fallback(mock_run):
    mock_run.side_effect = ValueError("API key not valid. Please pass a valid API key.")
    
    student_id = str(uuid4())
    resume_text = "John Doe. CS student. CGPA 9.0. Skills: Python, React, and Git. Projects: Chatbot." * 3

    profile = extract_student_profile(student_id, resume_text)

    assert isinstance(profile, StudentProfile)
    assert profile.extraction_method == "fallback"
    assert profile.overall_confidence == 0.1


# 3. Test Invalid API Key Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_invalid_api_key_fallback(mock_run):
    mock_run.side_effect = ClientError(400, {"error": {"message": "API key not valid"}})
    
    student_id = str(uuid4())
    resume_text = "John Doe. CS student. CGPA 9.0. Skills: Python, React, and Git. Projects: Chatbot." * 3

    profile = extract_student_profile(student_id, resume_text)

    assert isinstance(profile, StudentProfile)
    assert profile.extraction_method == "fallback"
    assert profile.overall_confidence == 0.1


# 4. Test 429 Quota Exceeded Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_quota_exceeded_fallback(mock_run):
    mock_run.side_effect = ClientError(429, {"error": {"message": "Quota exceeded"}})
    
    job_id = str(uuid4())
    jd_text = "Looking for a Software Intern. Skills required: Python, React, and Git. GPA: 8.0."

    output = extract_hiring_requirements(job_id, jd_text)

    assert isinstance(output, CompanyIntelligenceOutput)
    assert output.extraction_method == "fallback"
    assert output.overall_confidence == 0.1


# 5. Test 503 Service Unavailable Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_service_unavailable_fallback(mock_run):
    mock_run.side_effect = ClientError(503, {"error": {"message": "Service unavailable"}})
    
    job_id = str(uuid4())
    jd_text = "Looking for a Software Intern. Skills required: Python, React, and Git. GPA: 8.0."

    output = extract_hiring_requirements(job_id, jd_text)

    assert isinstance(output, CompanyIntelligenceOutput)
    assert output.extraction_method == "fallback"
    assert output.overall_confidence == 0.1


# 6. Test Timeout Exception Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_timeout_fallback(mock_run):
    # Simulate timeout inside the thread pool executor run by raising TimeoutError
    mock_run.side_effect = concurrent.futures.TimeoutError("Timeout occurred")

    student_id = str(uuid4())
    resume_text = "John Doe. CS student. CGPA 9.0. Skills: Python, React, and Git. Projects: Chatbot." * 3

    profile = extract_student_profile(student_id, resume_text)

    assert isinstance(profile, StudentProfile)
    assert profile.extraction_method == "fallback"
    assert profile.overall_confidence == 0.1


# 7. Test JSON Parsing Failure Fallback
@patch("google.adk.runners.InMemoryRunner.run")
def test_json_parsing_failure_fallback(mock_run):
    # Return output string that is not a valid JSON representation of StudentProfile
    mock_run.return_value = [MockEvent(output="{invalid_json_string")]

    student_id = str(uuid4())
    resume_text = "John Doe. CS student. CGPA 9.0. Skills: Python, React, and Git. Projects: Chatbot." * 3

    profile = extract_student_profile(student_id, resume_text)

    assert isinstance(profile, StudentProfile)
    assert profile.extraction_method == "fallback"
    assert profile.overall_confidence == 0.1


# 8. Test Orchestrator Pipeline Returns SUCCESS or PARTIAL_SUCCESS on Gemini failure
@patch("google.adk.runners.InMemoryRunner.run")
def test_pipeline_preserves_execution_on_gemini_failure(mock_run):
    # Force Gemini to fail so fallback is triggered in both Student and Company agents
    mock_run.side_effect = Exception("Gemini Connection Error")

    student_id = str(uuid4())
    job_id = str(uuid4())
    resume_text = "John Doe. CS student. CGPA 9.0. Skills: Python, React, and Git. Projects: Chatbot." * 3
    jd_text = "Looking for a Software Intern. Skills required: Python, React, and Git. GPA: 8.0."

    res = run_full_placement_analysis(student_id, resume_text, job_id, jd_text)

    assert isinstance(res, PlacementAnalysisResult)
    # Since fallback matching runs successfully, pipeline status is SUCCESS or PARTIAL_SUCCESS
    assert res.pipeline_status in [PipelineStatusEnum.SUCCESS, PipelineStatusEnum.PARTIAL_SUCCESS]
    assert res.student_profile is not None
    assert res.student_profile.extraction_method == "fallback"
    assert res.hiring_requirements is not None
    assert res.hiring_requirements.extraction_method == "fallback"
    assert res.match_result is not None
