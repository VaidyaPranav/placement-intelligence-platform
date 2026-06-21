# System Contracts Specification: Placement Intelligence Platform (PIP)
## Spec-Driven Development, API Contracts, Agent Interfaces, and Validation Specifications

---

## SECTION 1 — Core Entities

This section defines the attributes and validation rules for all system data structures.

### 1. Student
*   **Description:** Represents a registered student in the university placement system.
*   **Required Fields:** `id` (UUIDv4), `email` (RFC 5322 Email), `first_name` (String), `last_name` (String), `department` (Enum: `CS`, `IT`, `ECE`, `EE`, `ME`), `graduation_year` (Integer, $\ge 2026$).
*   **Optional Fields:** `phone` (E.164 String), `portfolio_url` (URI), `github_username` (Alphanumeric String).
*   **Validation Rules:** `email` must be unique; `graduation_year` must not be more than 4 years in the future.

### 2. Recruiter
*   **Description:** Represents an employer user looking to source talent.
*   **Required Fields:** `id` (UUIDv4), `email` (RFC 5322 Email), `company_name` (String), `role` (Enum: `HR_LEAD`, `SOURCER`).
*   **Optional Fields:** `website_url` (URI), `phone` (E.164 String).
*   **Validation Rules:** `email` must be unique.

### 3. JobDescription
*   **Description:** Details a hiring role posted by a recruiter.
*   **Required Fields:** `id` (UUIDv4), `recruiter_id` (UUIDv4), `role_title` (String), `raw_text` (String), `skills_required` (Array of Strings, $\ge 1$ item).
*   **Optional Fields:** `min_gpa` (Float, $0.0 \le x \le 10.0$), `experience_months` (Integer, $\ge 0$).
*   **Validation Rules:** `skills_required` must consist of valid tech-tags.

### 4. StudentProfile
*   **Description:** Structured portfolio of a student extracted from their resume and online links.
*   **Required Fields:** `student_id` (UUIDv4), `skills` (Array of tech-tags), `projects` (Array of Project objects).
*   **Optional Fields:** `courses` (Array of String course codes), `certifications` (Array of Strings).
*   **Validation Rules:** Projects must contain `title` and `complexity_score` ($1 \le x \le 10$).

### 5. MatchResult
*   **Description:** Stores the comparison score between a student and a job opening.
*   **Required Fields:** `match_id` (UUIDv4), `student_id` (UUIDv4), `job_id` (UUIDv4), `overall_match_score` (Float, $0.0 \le x \le 100.0$), `confidence_level` (Enum: `HIGH`, `MEDIUM`, `LOW`).
*   **Optional Fields:** `match_justification` (String).
*   **Validation Rules:** Matches must be recalculated if the underlying student profile is modified.

### 6. SkillGapReport
*   **Description:** Identifies specific gaps causing a student not to match a job perfectly.
*   **Required Fields:** `student_id` (UUIDv4), `job_id` (UUIDv4), `missing_skills` (Array of tech-tags), `severity` (Enum: `BLOCKER`, `RECOMMENDED`, `OPTIONAL`).
*   **Optional Fields:** `gap_explanation` (String).
*   **Validation Rules:** `missing_skills` must be the set difference between the job requirements and the student profile.

### 7. Roadmap
*   **Description:** A personalized training path created for a student to address identified skill gaps.
*   **Required Fields:** `roadmap_id` (UUIDv4), `student_id` (UUIDv4), `target_job_id` (UUIDv4), `weekly_milestones` (Array of Milestone objects, $\ge 1$).
*   **Optional Fields:** `estimated_hours` (Integer).
*   **Validation Rules:** Roadmap links must be safety-inspected.

### 8. InterviewSession
*   **Description:** Log of an interactive mock interview practice session.
*   **Required Fields:** `session_id` (UUIDv4), `student_id` (UUIDv4), `job_id` (UUIDv4), `transcripts` (Array of ChatMessage objects), `status` (Enum: `ACTIVE`, `COMPLETED`).
*   **Optional Fields:** `final_scorecard` (JSON).
*   **Validation Rules:** Transcript cannot exceed 50 conversation turns.

### 9. ReadinessScore
*   **Description:** The centralized metric indicating student placement readiness.
*   **Required Fields:** `student_id` (UUIDv4), `overall_score` (Integer, $0 \le x \le 100$), `breakdown` (ReadinessBreakdown Object), `updated_at` (Datetime).
*   **Optional Fields:** `text_summary` (String).
*   **Validation Rules:** Scores must update automatically when project or interview logs change.

### 10. SimulationResult
*   **Description:** Output of a hypothetical skill simulation.
*   **Required Fields:** `student_id` (UUIDv4), `target_job_id` (UUIDv4), `added_skills` (Array of tech-tags), `original_score` (Float), `simulated_score` (Float).
*   **Optional Fields:** `explanation` (String).
*   **Validation Rules:** Scores must match those of a cloned ranking loop.

### 11. AuditLog
*   **Description:** Ledger of security, overrides, and administrative modifications.
*   **Required Fields:** `log_id` (UUIDv4), `timestamp` (Datetime), `actor_id` (UUIDv4), `actor_role` (Enum: `SYSTEM`, `ADMIN`, `PLACEMENT_OFFICER`), `action_type` (String).
*   **Optional Fields:** `diff_payload` (JSON).
*   **Validation Rules:** Append-only ledger. No edits or deletions allowed.

---

## SECTION 2 — JSON Schemas

These production-quality JSON schemas are used to validate payloads at boundaries.

### 2.1. `student_profile.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StudentProfile",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "skills": {
      "type": "array",
      "items": { "type": "string" },
      "uniqueItems": true
    },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "description": { "type": "string" },
          "complexity_score": { "type": "integer", "minimum": 1, "maximum": 10 }
        },
        "required": ["title", "complexity_score"]
      }
    }
  },
  "required": ["student_id", "skills", "projects"]
}
```

### 2.2. `job_description.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "JobDescription",
  "type": "object",
  "properties": {
    "job_id": { "type": "string", "format": "uuid" },
    "role_title": { "type": "string" },
    "skills_required": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "min_gpa": { "type": "number", "minimum": 0.0, "maximum": 10.0 }
  },
  "required": ["job_id", "role_title", "skills_required"]
}
```

### 2.3. `match_result.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MatchResult",
  "type": "object",
  "properties": {
    "match_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "job_id": { "type": "string", "format": "uuid" },
    "overall_match_score": { "type": "number", "minimum": 0.0, "maximum": 100.0 },
    "confidence_level": { "type": "string", "enum": ["HIGH", "MEDIUM", "LOW"] },
    "explanation": { "type": "string" }
  },
  "required": ["match_id", "student_id", "job_id", "overall_match_score", "confidence_level"]
}
```

### 2.4. `skill_gap_report.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SkillGapReport",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "job_id": { "type": "string", "format": "uuid" },
    "missing_skills": { "type": "array", "items": { "type": "string" } },
    "severity": { "type": "string", "enum": ["BLOCKER", "RECOMMENDED", "OPTIONAL"] }
  },
  "required": ["student_id", "job_id", "missing_skills", "severity"]
}
```

### 2.5. `roadmap.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Roadmap",
  "type": "object",
  "properties": {
    "roadmap_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "weekly_milestones": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "week": { "type": "integer" },
          "milestone_title": { "type": "string" },
          "topics": { "type": "array", "items": { "type": "string" } },
          "resource_links": { "type": "array", "items": { "type": "string", "format": "uri" } }
        },
        "required": ["week", "milestone_title", "topics"]
      }
    }
  },
  "required": ["roadmap_id", "student_id", "weekly_milestones"]
}
```

### 2.6. `interview_session.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InterviewSession",
  "type": "object",
  "properties": {
    "session_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "status": { "type": "string", "enum": ["ACTIVE", "COMPLETED"] },
    "transcript": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "sender": { "type": "string", "enum": ["INTERVIEWER", "STUDENT"] },
          "text": { "type": "string" }
        },
        "required": ["sender", "text"]
      }
    }
  },
  "required": ["session_id", "student_id", "status", "transcript"]
}
```

### 2.7. `readiness_score.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReadinessScore",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "overall_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "breakdown": {
      "type": "object",
      "properties": {
        "technical": { "type": "integer", "minimum": 0, "maximum": 100 },
        "projects": { "type": "integer", "minimum": 0, "maximum": 100 },
        "communication": { "type": "integer", "minimum": 0, "maximum": 100 },
        "interview": { "type": "integer", "minimum": 0, "maximum": 100 }
      },
      "required": ["technical", "projects", "communication", "interview"]
    }
  },
  "required": ["student_id", "overall_score", "breakdown"]
}
```

### 2.8. `simulation_result.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SimulationResult",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "target_job_id": { "type": "string", "format": "uuid" },
    "added_skills": { "type": "array", "items": { "type": "string" } },
    "original_score": { "type": "number" },
    "simulated_score": { "type": "number" }
  },
  "required": ["student_id", "target_job_id", "added_skills", "original_score", "simulated_score"]
}
```

### 2.9. `audit_log.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AuditLog",
  "type": "object",
  "properties": {
    "log_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "actor_id": { "type": "string", "format": "uuid" },
    "actor_role": { "type": "string", "enum": ["SYSTEM", "ADMIN", "PLACEMENT_OFFICER"] },
    "action_type": { "type": "string" },
    "payload": { "type": "object" }
  },
  "required": ["log_id", "timestamp", "actor_id", "actor_role", "action_type"]
}
```

---

## SECTION 3 — Agent Contracts

Contracts for all Google ADK based agents:

### 3.1. Company Intelligence Agent
*   **Purpose:** Extract structured hiring requirements from raw job descriptions.
*   **Input Schema:** `{"raw_jd_text": "string"}`
*   **Output Schema:** `job_description.json`
*   **Dependencies:** `Doc_MCP` (for text extraction from PDF format).
*   **Failure Conditions:** Document unreadable or no skills extracted.
*   **Success Criteria:** Standardized JSON object detailing tech stack and parameters.

### 3.2. Student Intelligence Agent
*   **Purpose:** Extract and structure student profiles from resumes.
*   **Input Schema:** `{"resume_pdf_url": "string"}`
*   **Output Schema:** `student_profile.json`
*   **Dependencies:** `Doc_MCP` (for PDF text layout reading).
*   **Failure Conditions:** Invalid file format, complete parsing failure.
*   **Success Criteria:** Valid JSON profile with parsed skills and projects.

### 3.3. Ranking Agent
*   **Purpose:** Match student profiles against job descriptions.
*   **Input Schema:** `{"student_profile": student_profile.json, "job_requirements": job_description.json}`
*   **Output Schema:** `match_result.json`
*   **Dependencies:** None.
*   **Failure Conditions:** Mismatched schemas or empty profile array.
*   **Success Criteria:** Valid match score (0-100) and confidence flag.

### 3.4. Skill Gap Agent
*   **Purpose:** Extract differences between candidate skills and target role requirements.
*   **Input Schema:** `{"student_skills": ["string"], "job_requirements": ["string"]}`
*   **Output Schema:** `skill_gap_report.json`
*   **Dependencies:** None.
*   **Failure Conditions:** Inputs missing.
*   **Success Criteria:** Outputs structured list of gaps with severity ratings.

### 3.5. Career Roadmap Agent
*   **Purpose:** Formulate structured learning plans.
*   **Input Schema:** `skill_gap_report.json`
*   **Output Schema:** `roadmap.json`
*   **Dependencies:** None (Uses preset internal resource databases).
*   **Failure Conditions:** No gaps identified, resource query fails.
*   **Success Criteria:** Returns weekly study milestones and links.

### 3.6. Interview Agent
*   **Purpose:** Administer interactive technical screenings.
*   **Input Schema:** `{"student_id": "uuid", "target_job_id": "uuid", "chat_history": []}`
*   **Output Schema:** `interview_session.json`
*   **Dependencies:** None.
*   **Failure Conditions:** Client connection drop, token context overflow.
*   **Success Criteria:** Conversational responses and scorecard updates.

### 3.7. Governance Agent
*   **Purpose:** Enforce institutional compliance and audit overrides.
*   **Input Schema:** `{"actor_id": "uuid", "action": "string", "payload": "object"}`
*   **Output Schema:** `{"status": "PASS/FAIL", "log_written": "boolean"}`
*   **Dependencies:** `DB_MCP` (to write audit log rows).
*   **Failure Conditions:** DB write failure.
*   **Success Criteria:** Successful transaction logging.

### 3.8. Evaluation Agent
*   **Purpose:** Grade and evaluate match score reasoning quality.
*   **Input Schema:** `{"match_result": match_result.json, "resume": "string"}`
*   **Output Schema:** `{"evaluation_score": "integer", "hallucination_flag": "boolean"}`
*   **Dependencies:** None.
*   **Failure Conditions:** Unresponsive model.
*   **Success Criteria:** Outputs validation score (1-5 scale).

### 3.9. Placement Readiness Agent
*   **Purpose:** Aggregate student readiness scores.
*   **Input Schema:** `{"student_id": "uuid", "components": {"tech": "int", "proj": "int", "comm": "int", "interview": "int"}}`
*   **Output Schema:** `readiness_score.json`
*   **Dependencies:** None.
*   **Failure Conditions:** Missing metrics.
*   **Success Criteria:** Generates overall score and detailed explanations.

---

## SECTION 4 — Agent-to-Agent Contracts

Data pipelines between cooperating worker agents.

### 4.1. Student Agent $\rightarrow$ Ranking Agent
*   **Trigger:** Resume is onboarded and recruiter queries candidate lists.
*   **Payload Schema:**
```json
{
  "event_type": "STUDENT_ONBOARDED",
  "student_id": "3b2e3f89-8d19-482a-9e12-32b0129e9282",
  "data": {
    "skills": ["Java", "Spring Boot", "SQL"],
    "projects": [
      {
        "title": "Online Pharmacy Store",
        "complexity_score": 6
      }
    ]
  }
}
```

### 4.2. Ranking Agent $\rightarrow$ Skill Gap Agent
*   **Trigger:** Candidate matching score is calculated.
*   **Payload Schema:**
```json
{
  "event_type": "GAP_ANALYSIS_REQUEST",
  "match_id": "8c01e23f-e145-42bf-9023-b1d98a72ef01",
  "candidate_skills": ["Java", "Spring Boot", "SQL"],
  "job_requirements": ["Java", "Spring Boot", "SQL", "Docker", "Kubernetes"]
}
```

### 4.3. Skill Gap Agent $\rightarrow$ Roadmap Agent
*   **Trigger:** Gaps are identified for a candidate.
*   **Payload Schema:**
```json
{
  "event_type": "GENERATE_ROADMAP",
  "student_id": "3b2e3f89-8d19-482a-9e12-32b0129e9282",
  "missing_skills": ["Docker", "Kubernetes"],
  "severity": "BLOCKER"
}
```

### 4.4. Roadmap Agent $\rightarrow$ Readiness Agent
*   **Trigger:** Student completes/updates roadmap milestones.
*   **Payload Schema:**
```json
{
  "event_type": "ROADMAP_UPDATED",
  "student_id": "3b2e3f89-8d19-482a-9e12-32b0129e9282",
  "completed_milestones": 3,
  "total_milestones": 4
}
```

---

## SECTION 5 — API Contracts

REST API specifications for the FastAPI backend.

### 5.1. Student APIs
*   **Upload Resume**
    *   *Method:* `POST`
    *   *Route:* `/api/students/resume`
    *   *Request Body:* Multipart form data containing `file` (PDF, max 5MB).
    *   *Response Body:* `student_profile.json`
    *   *Validation:* File extension must be `.pdf`.
    *   *Errors:* `400 Bad Request` (Invalid file type), `500 Server Error` (Parsing fails).
*   **Fetch Roadmap**
    *   *Method:* `GET`
    *   *Route:* `/api/students/{id}/roadmap`
    *   *Response Body:* `roadmap.json`
    *   *Errors:* `404 Not Found`.

### 5.2. Recruiter APIs
*   **Upload Job Description**
    *   *Method:* `POST`
    *   *Route:* `/api/recruiters/jobs`
    *   *Request Body:* `{"role_title": "string", "raw_text": "string"}`
    *   *Response Body:* `job_description.json`
    *   *Errors:* `422 Unprocessable Entity` (Empty body).
*   **Fetch Candidates**
    *   *Method:* `GET`
    *   *Route:* `/api/recruiters/jobs/{job_id}/candidates`
    *   *Response Body:* Array of `match_result.json` schemas.
    *   *Errors:* `403 Forbidden` (Pending placement officer approval).

### 5.3. Placement Officer APIs
*   **Approvals List**
    *   *Method:* `GET`
    *   *Route:* `/api/admin/shortlists/pending`
    *   *Response Body:* Array of matching shortlist records.
*   **Approve Shortlist**
    *   *Method:* `POST`
    *   *Route:* `/api/admin/shortlists/{job_id}/approve`
    *   *Request Body:* `{"approved_student_ids": ["string"]}`
    *   *Response Body:* `{"status": "SUCCESS"}`
    *   *Errors:* `401 Unauthorized`.

### 5.4. Simulation APIs
*   **Simulate Skill Match**
    *   *Method:* `POST`
    *   *Route:* `/api/students/{id}/simulate`
    *   *Request Body:* `{"target_job_id": "string", "added_skills": ["string"]}`
    *   *Response Body:* `simulation_result.json`
    *   *Validation:* `added_skills` cannot be empty.

---

## SECTION 6 — Placement Readiness Specification

Defines the mathematical modeling of the Placement Readiness index.

### 6.1. Formulas
$$\text{Readiness Score} = \text{round}\left( 0.30 \cdot T + 0.30 \cdot P + 0.20 \cdot C + 0.20 \cdot I \right)$$

Where:
*   $T = \text{Technical Score}$
*   $P = \text{Project Score}$
*   $C = \text{Communication Score}$
*   $I = \text{Interview Score}$

### 6.2. Component Rules
1.  **Technical Score ($T$):** Calculated as:
    $$T = \text{clip}\left( (\text{GPA} \cdot 10) + (\text{Certifications Count} \cdot 5), 0, 100 \right)$$
2.  **Project Score ($P$):** Scaled average of complexity:
    $$P = \frac{\sum_{i=1}^{n} \text{Complexity}_i}{n} \cdot 10$$
3.  **Communication Score ($C$):** Checked by NLP text statistics on mock transcripts:
    $$C = \text{clip}\left( 100 - (\text{Um/Uh counts} \cdot 2) - (\text{Sentence length variance penalties}), 0, 100 \right)$$
4.  **Interview Score ($I$):** Evaluated scorecard metrics:
    $$I = \text{Average grade assigned across active mock tests}$$

### 6.3. Explainability & Suggestions
*   If $P < 60$, suggestions must include: *"Add a project verifying a containerization or cloud deployment framework."*
*   If $I < 70$, suggestions must include: *"Schedule another mock interview focusing on Algorithms and Data Structures."*

---

## SECTION 7 — What-If Simulation Specification

Predictive analytics for hypothetical skill additions.

```
       +------------------------------------+
       |          Original State            | --> Score: 72%
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |           Simulated Run            |
       |  - Clone Profile                   |
       |  - Append: "AWS"                   |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |           Output Result            | --> Score: 88% (+16%)
       +------------------------------------+
```

### 7.1. Workflow
1.  **Read Original State:** Pull student data and current match score from database.
2.  **Clone Data:** Duplicate student profile into memory as a decoupled dictionary object.
3.  **Apply Hypothetical Skills:** Insert simulated skill tags (e.g. `["Docker", "AWS"]`) to the profile's skill array.
4.  **Evaluate Match:** Re-run the matching logic (implemented in the `Ranking Agent`) against target JD.
5.  **Evaluate Readiness:** Re-calculate the Readiness Score using the cloned parameters.
6.  **Calculate Score Delta:** $\Delta = \text{Simulated Score} - \text{Original Score}$.
7.  **Safety Check:** Governance Agent validates that the added skill corresponds to the target JD stack.

---

## SECTION 8 — Governance Rules

Operational constraints and security guardrails.

*   **PII Masking Rule:** Recruiter endpoints must replace student fields `first_name`, `last_name`, `email`, and `phone` with masked representations (e.g., `CANDIDATE_A87B`) until the candidate list is officially approved.
*   **Audit Logging Rule:** Every override action must write a record to `AUDIT_LOG` containing the actor ID, timestamp, target ID, original value, and modified value.
*   **HITL Override Rules:** Placement Officers can override candidate rankings. The original rank remains in the database for accuracy audit checks.

---

## SECTION 9 — Evaluation Specification

Validating match accuracy and reasoning.

### 9.1. Match Quality Metrics (Offline)
*   **Target Metric:** NDCG (Normalized Discounted Cumulative Gain)
    $$\text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$
*   NDCG must exceed $0.85$ on the Golden Sourcing Dataset.

### 9.2. LLM-as-a-Judge Evaluation (Online)
The system checks 10% of match explanations using the `Evaluation Agent` against these constraints:
1.  **Hallucination Check:** Do matched skills appear in the resume? (Y/N).
2.  **Grounding:** Are skills mapped to specific student projects? (Y/N).
3.  **Tone Validation:** Is the writing professional and objective? (Score 1-5).

---

## SECTION 10 — Gherkin Specifications

Complete Gherkin Behavior-Driven Development (BDD) specifications.

### 10.1. Resume Upload
```gherkin
Feature: Student Resume Onboarding
  Scenario: Successful PDF resume parse
    Given the student Ananya is logged into the portal
    When she uploads a valid PDF resume "ananya_resume.pdf"
    Then the Student Intelligence Agent parses the document
    And the database registers a new Student Profile with verified skills
```

### 10.2. Job Description Upload
```gherkin
Feature: Job Description Processing
  Scenario: Recruiter uploads a structured job post
    Given the recruiter Marcus is logged into his panel
    When he submits a job description for "Backend Engineer"
    Then the Company Intelligence Agent extracts required technical skills
    And the job requirements are saved successfully in the database
```

### 10.3. Candidate Ranking
```gherkin
Feature: Matching Candidates to Job Roles
  Scenario: Calculate match percentages for active postings
    Given a job posting has been successfully registered
    And candidate profiles exist in the system database
    When the system triggers the matching loop
    Then the Ranking Agent computes match scores for each student
```

### 10.4. Skill Gap Analysis
```gherkin
Feature: Identify missing competencies
  Scenario: Retrieve missing skills for matched profiles
    Given a candidate has matched a backend role with score 78%
    When the Skill Gap Agent compares profile skills to job requirements
    Then a list of missing skill gaps is generated with severity ratings
```

### 10.5. Roadmap Generation
```gherkin
Feature: Training roadmap creation
  Scenario: Generate study path to bridge gaps
    Given a candidate has missing requirements
    When the Career Roadmap Agent is invoked
    Then a weekly calendar of learning modules and resource links is returned
```

### 10.6. Placement Readiness Generation
```gherkin
Feature: Compute placement readiness
  Scenario: Recalculate readiness on updates
    Given Ananya has completed a roadmap milestone project
    When the Placement Readiness Agent gathers updated portfolio parameters
    Then her overall Placement Readiness Score increases proportionally
```

### 10.7. What-If Simulation
```gherkin
Feature: Simulating skill additions
  Scenario: Evaluate hypothetical skill upgrades
    Given a student profile has a match score of 72%
    When the student requests a simulation adding "Docker"
    Then the system clones the profile, appends the skill, and re-ranks it
    And returns the delta score and an explanation of the change
```

### 10.8. Mock Interview
```gherkin
Feature: Interactive screening tests
  Scenario: Administer a technical mock interview session
    Given a student starts a practice interview for a Node.js role
    When the Interview Agent posts a technical question
    And the student inputs a response
    Then the agent evaluates the response and updates the scorecard
```

### 10.9. Governance Approval
```gherkin
Feature: Governance shortlist oversight
  Scenario: Intercept candidate shortlists
    Given the matching run completes for a Cloud Specialist role
    When the shortlist is compiled by the Ranking Agent
    Then the Governance Agent intercepts the list and flags it as pending approval
```

### 10.10. Recruiter Analytics
```gherkin
Feature: Recruiter analytics generation
  Scenario: Compute pool metrics
    Given a recruiter opens a job dashboard page
    When the backend runs aggregation queries on matches
    Then average match scores, candidate pool sizes, and missing skills are returned
```

---

## SECTION 11 — MVP vs Future Scope

Decoupling current MVP milestones from future roadmap expansions.

```
       +------------------------------------+
       |            MVP Scope               |
       |  - Basic PDF / resume extraction   |
       |  - Match scores & Roadmap outputs  |
       |  - What-If simulations             |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |            Future Scope            |
       |  - Full GitHub validation checks   |
       |  - Live audio mock interviews      |
       |  - Multi-region DB replications    |
       +------------------------------------+
```

*   **MVP Scope (Current):** Single-container FastAPI deployment; document parsing; in-memory What-If simulations; basic mock interview chat rooms; offline evaluation matching.
*   **Post-MVP (Next Phase):** Full repository crawler integration; automated resume rewrite tips; offline bias validation.
*   **Future Enhancements (Long-term):** Real-time voice interview processing; full college LMS sync; automated university calendar alerts.

---

## SECTION 12 — Conclusion

This system contract specification establishes the verification, schema, and API contracts for the **Placement Intelligence Platform (PIP)**. By referencing the JSON schemas, API routes, and scoring rules defined here, development can proceed with a single source of truth, aligning the codebase with Kaggle Hackathon parameters.
