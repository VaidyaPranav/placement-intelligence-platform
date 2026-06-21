# API Integration Tests

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import PIPELINE_VERSION

client = TestClient(app)

DUMMY_STUDENT_ID = "a2a0a3b7-9adb-4031-ae78-e80afb96c3b2"
DUMMY_RESUME_TEXT = (
    "Prep Student Resume.\n"
    "CGPA is 9.0. Department is Computer Science.\n"
    "Skills: React, Python, Git.\n"
    "This is a longer resume text designed to satisfy the length verification constraints of at least 100 characters."
)

DUMMY_JOB_ID = "b2b0b3b7-9adb-4031-ae78-e80afb96c3b2"
DUMMY_JOB_DESCRIPTION = (
    "We are looking for a Software Developer. "
    "Required skills: React, Docker. Preferred skills: AWS. "
    "Minimum CGPA: 8.0. Candidates must have strong communication skills."
)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Placement Intelligence Platform"
    assert data["version"] == PIPELINE_VERSION
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["pipeline_version"] == PIPELINE_VERSION


def test_student_analyze_endpoint():
    # Valid call
    payload = {
        "student_id": DUMMY_STUDENT_ID,
        "resume_text": DUMMY_RESUME_TEXT
    }
    response = client.post("/api/v1/student/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == DUMMY_STUDENT_ID
    assert "React" in data["skills"]

    # Invalid UUID (triggers ValueError -> HTTP 400)
    invalid_uuid_payload = {
        "student_id": "not-a-valid-uuid",
        "resume_text": DUMMY_RESUME_TEXT
    }
    response = client.post("/api/v1/student/analyze", json=invalid_uuid_payload)
    assert response.status_code == 400
    assert "valid UUIDv4" in response.json()["detail"]

    # Too short resume (triggers ValueError -> HTTP 400)
    short_resume_payload = {
        "student_id": DUMMY_STUDENT_ID,
        "resume_text": "Short resume"
    }
    response = client.post("/api/v1/student/analyze", json=short_resume_payload)
    assert response.status_code == 400
    assert "at least 100 characters" in response.json()["detail"]


def test_job_analyze_endpoint():
    payload = {
        "job_id": DUMMY_JOB_ID,
        "job_description": DUMMY_JOB_DESCRIPTION
    }
    response = client.post("/api/v1/job/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == DUMMY_JOB_ID
    assert "React" in data["required_skills"]

    # Invalid job_id UUID
    invalid_uuid_payload = {
        "job_id": "not-a-valid-uuid",
        "job_description": DUMMY_JOB_DESCRIPTION
    }
    response = client.post("/api/v1/job/analyze", json=invalid_uuid_payload)
    assert response.status_code == 400
    assert "valid UUIDv4" in response.json()["detail"]


def test_entire_agent_chain_endpoints():
    # 1. Analyze student
    student_res = client.post("/api/v1/student/analyze", json={
        "student_id": DUMMY_STUDENT_ID,
        "resume_text": DUMMY_RESUME_TEXT
    })
    assert student_res.status_code == 200
    student_profile = student_res.json()

    # 2. Analyze job
    job_res = client.post("/api/v1/job/analyze", json={
        "job_id": DUMMY_JOB_ID,
        "job_description": DUMMY_JOB_DESCRIPTION
    })
    assert job_res.status_code == 200
    hiring_requirements = job_res.json()

    # 3. Match
    match_payload = {
        "student_profile": student_profile,
        "hiring_requirements": hiring_requirements
    }
    match_res = client.post("/api/v1/match", json=match_payload)
    assert match_res.status_code == 200
    match_result = match_res.json()
    assert "match_score" in match_result

    # 4. Skill Gap
    gap_payload = {
        "student_profile": student_profile,
        "hiring_requirements": hiring_requirements,
        "match_result": match_result
    }
    gap_res = client.post("/api/v1/skill-gap", json=gap_payload)
    assert gap_res.status_code == 200
    skill_gap_report = gap_res.json()
    assert "gap_score" in skill_gap_report

    # 5. Roadmap
    roadmap_payload = {
        "student_profile": student_profile,
        "skill_gap_report": skill_gap_report
    }
    roadmap_res = client.post("/api/v1/roadmap", json=roadmap_payload)
    assert roadmap_res.status_code == 200
    career_roadmap = roadmap_res.json()
    assert "roadmap_weeks" in career_roadmap

    # 6. Interview
    interview_payload = {
        "student_profile": student_profile,
        "hiring_requirements": hiring_requirements,
        "match_result": match_result,
        "skill_gap_report": skill_gap_report
    }
    interview_res = client.post("/api/v1/interview", json=interview_payload)
    assert interview_res.status_code == 200
    interview_report = interview_res.json()
    assert "technical_questions" in interview_report


def test_full_analysis_endpoint():
    payload = {
        "student_id": DUMMY_STUDENT_ID,
        "resume_text": DUMMY_RESUME_TEXT,
        "job_id": DUMMY_JOB_ID,
        "job_description": DUMMY_JOB_DESCRIPTION
    }
    response = client.post("/api/v1/full-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["pipeline_status"] == "SUCCESS"
    assert len(data["errors"]) == 0
    assert len(data["execution_steps_completed"]) == 6
    assert len(data["execution_steps_failed"]) == 0
    
    assert data["student_profile"] is not None
    assert data["hiring_requirements"] is not None
    assert data["match_result"] is not None
    assert data["skill_gap_report"] is not None
    assert data["career_roadmap"] is not None
    assert data["interview_report"] is not None
    assert data["pipeline_version"] == PIPELINE_VERSION
    assert "total_execution_time_seconds" in data


def test_match_validation_error():
    # Sending empty body should trigger 422 Unprocessable Entity
    response = client.post("/api/v1/match", json={})
    assert response.status_code == 422


def test_skill_gap_validation_error():
    # Malformed data triggers 422
    response = client.post("/api/v1/skill-gap", json={"student_profile": {}})
    assert response.status_code == 422


def test_roadmap_validation_error():
    # Malformed data triggers 422
    response = client.post("/api/v1/roadmap", json={"skill_gap_report": {}})
    assert response.status_code == 422


def test_interview_validation_error():
    # Malformed data triggers 422
    response = client.post("/api/v1/interview", json={"student_profile": {}})
    assert response.status_code == 422

