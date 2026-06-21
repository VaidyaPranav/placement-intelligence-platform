# Placement Intelligence Platform API Documentation

This document describes all API endpoints exposed by the FastAPI layer of the Placement Intelligence Platform (PIP).

## Base URL

By default, the backend API is hosted at:
`http://localhost:8000`

All endpoints (except root and health) are prefixed with `/api/v1`.

---

## 1. Root & Health Check Endpoints

### GET /
Returns service metadata.

*   **Request URL:** `GET http://localhost:8000/`
*   **Response (200 OK):**
    ```json
    {
      "service": "Placement Intelligence Platform",
      "version": "1.0.0",
      "status": "running"
    }
    ```

### GET /health
Returns the platform health status. Used by frontend status checkers and Docker health probes.

*   **Request URL:** `GET http://localhost:8000/health`
*   **Response (200 OK):**
    ```json
    {
      "status": "healthy",
      "pipeline_version": "1.0.0"
    }
    ```

---

## 2. Student Analysis Endpoint

### POST /api/v1/student/analyze
Extracts a structured student profile from a raw resume.

*   **Request Schema:**
    ```json
    {
      "student_id": "string (UUIDv4)",
      "resume_text": "string (at least 100 characters)"
    }
    ```
*   **Example Request:**
    ```json
    {
      "student_id": "d040854d-7bc7-43c7-9572-c7f773b063ee",
      "resume_text": "John Doe. Skills: React, Node.js, Python, Git. Experienced in building web apps. CGPA: 8.5"
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "student_id": "d040854d-7bc7-43c7-9572-c7f773b063ee",
      "skills": ["React", "Node.js", "Python", "Git"],
      "experience_years": 0.0,
      "certifications": [],
      "education": [
        {
          "degree": "B.Tech",
          "cgpa": 8.5
        }
      ]
    }
    ```

---

## 3. Job Analysis Endpoint

### POST /api/v1/job/analyze
Extracts target roles and hiring requirements from a job description.

*   **Request Schema:**
    ```json
    {
      "job_id": "string (UUIDv4)",
      "job_description": "string (at least 50 characters)"
    }
    ```
*   **Example Request:**
    ```json
    {
      "job_id": "f5f0b5cc-4813-40e1-bb96-d8a15998a69a",
      "job_description": "Looking for a Software Intern. Required skills: React, Node.js, MySQL, Git. Preferred: Docker."
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "job_id": "f5f0b5cc-4813-40e1-bb96-d8a15998a69a",
      "target_role": "Software Intern",
      "required_skills": ["React", "Node.js", "MySQL", "Git"],
      "preferred_skills": ["Docker"],
      "min_experience_years": 0.0
    }
    ```

---

## 4. Match Endpoint

### POST /api/v1/match
Matches a student profile against hiring requirements to calculate a score.

*   **Request Schema:**
    ```json
    {
      "student_profile": { ... },
      "hiring_requirements": { ... }
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "overall_match_score": 75.0,
      "skills_match_score": 80.0,
      "experience_match_score": 100.0,
      "education_match_score": 100.0,
      "ranking_explanation": "The candidate has most of the required skills including React, Node.js and Git."
    }
    ```

---

## 5. Skill Gap Analysis Endpoint

### POST /api/v1/skill-gap
Computes skill gaps categorizing missing, overlapping, and extra skills.

*   **Request Schema:**
    ```json
    {
      "student_profile": { ... },
      "hiring_requirements": { ... },
      "match_result": { ... }
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "missing_skills": ["MySQL"],
      "overlapping_skills": ["React", "Node.js", "Git"],
      "extra_skills": ["Python"],
      "recommendations": ["Learn MySQL to cover all core required skills."]
    }
    ```

---

## 6. Career Roadmap Endpoint

### POST /api/v1/roadmap
Generates a structured learning roadmap to bridge identified skill gaps.

*   **Request Schema:**
    ```json
    {
      "student_profile": { ... },
      "skill_gap_report": { ... }
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "milestones": [
        {
          "week_number": 1,
          "topics": ["MySQL Basics", "Relational Database Design"],
          "resources": ["W3Schools SQL Tutorial", "Khan Academy SQL"],
          "target_hours": 10
        }
      ],
      "estimated_completion_weeks": 2
    }
    ```

---

## 7. Interview Preparation Endpoint

### POST /api/v1/interview
Generates a role-specific interview preparation pack.

*   **Request Schema:**
    ```json
    {
      "student_profile": { ... },
      "hiring_requirements": { ... },
      "match_result": { ... },
      "skill_gap_report": { ... }
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "questions": [
        {
          "question": "Explain how React State differs from Props.",
          "skill": "React",
          "difficulty": "EASY",
          "expected_answer": "Props are read-only and passed from parent. State is local and managed by component.",
          "evaluation_rubric": "Look for hooks references (useState) and lifecycle differences."
        }
      ]
    }
    ```

---

## 8. Full Analysis Pipeline Endpoint

### POST /api/v1/full-analysis
Executes the full pipeline orchestrating all six intelligence agents in sequence.

*   **Request Schema:**
    ```json
    {
      "student_id": "string (UUIDv4)",
      "resume_text": "string",
      "job_id": "string (UUIDv4)",
      "job_description": "string"
    }
    ```
*   **Example Response (200 OK):**
    ```json
    {
      "student_profile": { ... },
      "hiring_requirements": { ... },
      "match_result": { ... },
      "skill_gap_report": { ... },
      "career_roadmap": { ... },
      "interview_report": { ... },
      "pipeline_status": "SUCCESS",
      "errors": [],
      "execution_steps_completed": [
        "student_agent",
        "company_agent",
        "ranking_agent",
        "skill_gap_agent",
        "career_roadmap_agent",
        "interview_agent"
      ],
      "execution_steps_failed": [],
      "total_execution_time_seconds": 0.45,
      "pipeline_version": "1.0.0"
    }
    ```

---

## 9. AI Status Endpoint

### GET /api/v1/ai-status
Returns the real-time configuration and connectivity status of the Gemini API and agent enrichment/fallback flags.

*   **Request URL:** `GET http://localhost:8000/api/v1/ai-status`
*   **Response (200 OK):**
    ```json
    {
      "llm_enrichment_enabled": true,
      "fallback_enabled": true,
      "gemini_api_configured": true,
      "status": "AI_ACTIVE"
    }
    ```
*   **Response Fields:**
    *   `llm_enrichment_enabled`: (boolean) Indicates if LLM-based profile enrichment is turned on.
    *   `fallback_enabled`: (boolean) Indicates if fallback to deterministic models is enabled when LLM extraction fails.
    *   `gemini_api_configured`: (boolean) Indicates if `GOOGLE_API_KEY` is present in the environment variables.
    *   `status`: (string) Current operational mode of Gemini AI. Can be:
        *   `"AI_ACTIVE"`: Key configured and connectivity test succeeded.
        *   `"FALLBACK_MODE"`: Key configured or missing, but fallback is enabled and we are actively falling back to deterministic extraction.
        *   `"API_KEY_MISSING"`: Key missing and fallback disabled or unavailable.

