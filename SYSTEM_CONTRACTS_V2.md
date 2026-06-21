# System Contracts Specification V2: Targeted Refinements
## Placement Intelligence Platform (PIP) — Contract Refinements

---

## SECTION 1 — Refined & New Core Entities

This section updates the `StudentProfile` and `ReadinessScore` definitions, and introduces the new `ReadinessHistory` and `RecruiterAnalytics` entities.

### 1.4. StudentProfile (Refined)
*   **Description:** Extended structured student portfolio containing academic achievements, GitHub links, and professional profiles.
*   **Required Fields:**
    *   `student_id` (UUIDv4)
    *   `department` (Enum: `CS`, `IT`, `ECE`, `EE`, `ME`)
    *   `cgpa` (Float, $0.0 \le x \le 10.0$)
    *   `skills` (Array of tech-tags)
    *   `projects` (Array of Project objects containing `title` and `complexity_score`)
*   **Optional Fields:**
    *   `certifications` (Array of Certification objects containing `name` and `issuer`)
    *   `github_url` (URI)
    *   `portfolio_url` (URI)
    *   `linkedin_url` (URI)
    *   `achievements` (Array of Strings)
    *   `internships` (Array of Internship objects containing `company`, `role`, and `duration_months`)
*   **Validation Rules:** `cgpa` must be bounded between $0.0$ and $10.0$; `github_url`, `portfolio_url`, and `linkedin_url` must be valid URIs if provided.

### 1.9. ReadinessScore (Refined)
*   **Description:** Central metric calculated by the Placement Readiness Agent incorporating certification metrics.
*   **Required Fields:**
    *   `student_id` (UUIDv4)
    *   `overall_score` (Integer, $0 \le x \le 100$)
    *   `breakdown` (ReadinessBreakdown Object including `technical`, `projects`, `communication`, `interview`, and `certifications` parameters)
    *   `updated_at` (Datetime)
*   **Optional Fields:** `text_summary` (String).
*   **Validation Rules:** Component values must be integers between 0 and 100.

### 1.12. ReadinessHistory (New)
*   **Description:** Tracks historical placement readiness progression to render progress trends in student and administrative views.
*   **Required Fields:**
    *   `student_id` (UUIDv4)
    *   `date` (ISO 8601 Date format: `YYYY-MM-DD`)
    *   `readiness_score` (Integer, $0 \le x \le 100$)
    *   `readiness_breakdown` (JSON object detailing the five sub-scores)
*   **Optional Fields:** None.
*   **Validation Rules:** Rows are immutable; only append operations allowed.

### 1.13. RecruiterAnalytics (New)
*   **Description:** Aggregated pool metrics displayed on the Recruiter Intelligence Dashboard.
*   **Required Fields:**
    *   `candidate_pool_size` (Integer, $\ge 0$)
    *   `average_match_score` (Float, $0.0 \le x \le 100.0$)
    *   `average_readiness_score` (Float, $0.0 \le x \le 100.0$)
    *   `top_missing_skills` (Array of objects detailing `skill` and `frequency_percentage`)
    *   `most_competitive_department` (String)
    *   `shortlist_confidence` (Float, $0.0 \le x \le 100.0$)
*   **Optional Fields:** None.
*   **Validation Rules:** Calculated dynamically from matching runs.

---

## SECTION 2 — Refined & New JSON Schemas

### 2.1. `student_profile.json` (Refined)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StudentProfile",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "department": { "type": "string", "enum": ["CS", "IT", "ECE", "EE", "ME"] },
    "cgpa": { "type": "number", "minimum": 0.0, "maximum": 10.0 },
    "skills": { "type": "array", "items": { "type": "string" }, "uniqueItems": true },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "complexity_score": { "type": "integer", "minimum": 1, "maximum": 10 }
        },
        "required": ["title", "complexity_score"]
      }
    },
    "certifications": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "issuer": { "type": "string" }
        },
        "required": ["name", "issuer"]
      }
    },
    "github_url": { "type": "string", "format": "uri" },
    "portfolio_url": { "type": "string", "format": "uri" },
    "linkedin_url": { "type": "string", "format": "uri" },
    "achievements": { "type": "array", "items": { "type": "string" } },
    "internships": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "company": { "type": "string" },
          "role": { "type": "string" },
          "duration_months": { "type": "integer", "minimum": 1 }
        },
        "required": ["company", "role", "duration_months"]
      }
    }
  },
  "required": ["student_id", "department", "cgpa", "skills", "projects"]
}
```

### 2.7. `readiness_score.json` (Refined)
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
        "interview": { "type": "integer", "minimum": 0, "maximum": 100 },
        "certifications": { "type": "integer", "minimum": 0, "maximum": 100 }
      },
      "required": ["technical", "projects", "communication", "interview", "certifications"]
    }
  },
  "required": ["student_id", "overall_score", "breakdown"]
}
```

### 2.10. `readiness_history.json` (New)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReadinessHistory",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "date": { "type": "string", "format": "date" },
    "readiness_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "readiness_breakdown": {
      "type": "object",
      "properties": {
        "technical": { "type": "integer" },
        "projects": { "type": "integer" },
        "communication": { "type": "integer" },
        "interview": { "type": "integer" },
        "certifications": { "type": "integer" }
      },
      "required": ["technical", "projects", "communication", "interview", "certifications"]
    }
  },
  "required": ["student_id", "date", "readiness_score", "readiness_breakdown"]
}
```

### 2.11. `recruiter_analytics.json` (New)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RecruiterAnalytics",
  "type": "object",
  "properties": {
    "candidate_pool_size": { "type": "integer" },
    "average_match_score": { "type": "number" },
    "average_readiness_score": { "type": "number" },
    "top_missing_skills": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "skill": { "type": "string" },
          "frequency_percentage": { "type": "number" }
        },
        "required": ["skill", "frequency_percentage"]
      }
    },
    "most_competitive_department": { "type": "string" },
    "shortlist_confidence": { "type": "number" }
  },
  "required": [
    "candidate_pool_size",
    "average_match_score",
    "average_readiness_score",
    "top_missing_skills",
    "most_competitive_department",
    "shortlist_confidence"
  ]
}
```

---

## SECTION 3 — Upgraded Placement Readiness Specification

We refine the readiness scoring model to assign explicit weighting to student industry certifications.

### 3.1. Unified Formula
$$\text{Readiness Score} = \text{round}\left( 0.30 \cdot T + 0.25 \cdot P + 0.15 \cdot C + 0.20 \cdot I + 0.10 \cdot Cert \right)$$

### 3.2. Certification Score ($Cert$) Algorithm
The Certification Score ($Cert$) is determined by checking the certifications array against a verified registry of industry-recognized cloud, database, and software credentials:
$$Cert = \text{clip}\left( \sum_{i=1}^{m} \text{Weight}(\text{Certification}_i), 0, 100 \right)$$

*   **Tier 1 Credentials (40 points each):** Complete technical certifications (e.g. AWS Certified Solutions Architect, Google Cloud Professional Cloud Architect, OCP Java SE).
*   **Tier 2 Credentials (20 points each):** Fundamental cloud certifications (e.g. AWS Cloud Practitioner, OCI Foundations, Azure Fundamentals).
*   **Tier 3 Credentials (10 points each):** Course completion certificates (e.g. Coursera Deep Learning Specialization).

---

## SECTION 4 — Upgraded What-If Simulation Specification

We extend the simulation capability to test the impact of multiple factors.

### 4.1. Simulation Inputs Payload
The system processes multi-dimensional simulation requests conforming to this schema:
```json
{
  "target_job_id": "1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b",
  "simulation_parameters": {
    "added_skills": ["Docker"],
    "added_certifications": ["AWS Cloud Practitioner"],
    "new_project": {
      "title": "Cloud Deployment Pipeline",
      "complexity_score": 8
    },
    "simulated_score_improvements": {
      "interview": 15,
      "communication": 10
    }
  }
}
```

### 4.2. In-Memory Calculation Pipeline
1.  **Clone profile:** Copy current candidate DB attributes.
2.  **Apply parameters:**
    *   Append `added_skills` to `skills`.
    *   Append `added_certifications` to `certifications`.
    *   Append `new_project` to `projects`.
    *   Simulate score increases by adding delta values directly to original metrics: $I_{sim} = I_{orig} + 15$ and $C_{sim} = C_{orig} + 10$.
3.  **Run Evaluation:** Invoke the match scoring model on this mock profile.
4.  **Recalculate Readiness:** Apply the revised formula including the updated $Cert$, $P$, $C$, and $I$ components.

---

## SECTION 5 — Recruiter Analytics API

*   **Endpoint:** `GET /api/recruiters/jobs/{job_id}/analytics`
*   **Role Requirements:** Recruiter (Marcus) or Placement Officer (Meera).
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Response Payload:** `recruiter_analytics.json`
*   **Sample Response:**
```json
{
  "candidate_pool_size": 45,
  "average_match_score": 76.5,
  "average_readiness_score": 81.2,
  "top_missing_skills": [
    { "skill": "AWS", "frequency_percentage": 62.0 },
    { "skill": "Docker", "frequency_percentage": 45.5 }
  ],
  "most_competitive_department": "CS",
  "shortlist_confidence": 91.0
}
```

---

## SECTION 6 — Hardened Agent Execution Specifications

To guarantee execution integrity in production, all agents adhere to these strict contracts:

```
[ Input Payload ] --> [ Input validation ]
                            | (Pass)
                            v
                    [ Agent Loop ] <--- (Retry Policy on Exception)
                            | (Success)
                            v
[ Output Payload ] <-- [ Output validation ]
```

### 1. Company Intelligence Agent
*   **Input Validation:** Raw string must contain at least 50 characters.
*   **Output Validation:** Enforces matching key names in `job_description.json`.
*   **Retry Policy:** Retry 3 times on API latency exceptions (exponential backoff starting at 2s).
*   **Failure Recovery Strategy:** Revert to parsing using regex fallback heuristics if the LLM fails.
*   **Confidence Scoring:** Confidence rating based on the percentage of matching keywords found in the database.
*   **Explainability Requirements:** Must output which sentences in the JD triggered the extraction of each skill.

### 2. Student Intelligence Agent
*   **Input Validation:** Enforces correct PDF header signature validation.
*   **Output Validation:** Enforces schema structure in `student_profile.json`.
*   **Retry Policy:** Retry 2 times on connection timeouts.
*   **Failure Recovery Strategy:** Revert to parsing using direct PDF text extraction wrappers.
*   **Confidence Scoring:** Output parser validation confidence score.
*   **Explainability Requirements:** Map every extracted skill to a specific paragraph in the parsed PDF text.

### 3. Ranking Agent
*   **Input Validation:** Both inputs must match their respective JSON schemas.
*   **Output Validation:** Output must conform to `match_result.json`.
*   **Retry Policy:** Retry 2 times.
*   **Failure Recovery Strategy:** Revert to basic TF-IDF term matching algorithm.
*   **Confidence Scoring:** Calculates score confidence based on project alignment.
*   **Explainability Requirements:** Detail calculations for GPA, Project, and Skill weights.

### 4. Skill Gap Agent
*   **Input and Output Validation:** Enforces arrays of string parameters.
*   **Retry Policy:** No retries. Instantly calculate set-difference locally.
*   **Failure Recovery Strategy:** Fall back on pure Python set-difference calculations.
*   **Confidence Scoring:** Static $100\%$ confidence.
*   **Explainability Requirements:** Document matching vs missing sets.

### 5. Career Roadmap Agent
*   **Input Validation:** Enforces strict array validations for gap reports.
*   **Output Validation:** Validates JSON links against URL format specifications.
*   **Retry Policy:** Retry 3 times on resource fetch failures.
*   **Failure Recovery Strategy:** Load mock study templates corresponding to missing skills.
*   **Confidence Scoring:** Based on resource lookup matches.
*   **Explainability Requirements:** Explain the progression order of roadmap weeks.

### 6. Interview Agent
*   **Input Validation:** Must receive valid student IDs.
*   **Output Validation:** Ensures JSON transcript records are updated.
*   **Retry Policy:** Retry 2 times on LLM generation issues.
*   **Failure Recovery Strategy:** Load a static list of questions.
*   **Confidence Scoring:** Grades conversational metrics.
*   **Explainability Requirements:** Outline the criteria used to grade answers.

### 7. Governance Agent
*   **Input Validation:** Verify actor signatures and authorizations.
*   **Output Validation:** Outputs boolean status results.
*   **Retry Policy:** 3 retries on database transaction locks.
*   **Failure Recovery Strategy:** Block the transaction, notify the system administrator, and log the failure to a backup text file.
*   **Confidence Scoring:** Static $100\%$ confidence.
*   **Explainability Requirements:** Reference specific violated system rules.

### 8. Evaluation Agent
*   **Input Validation:** Enforce presence of match results and source text.
*   **Output Validation:** Enforce scores between 1 and 5.
*   **Retry Policy:** Retry 2 times.
*   **Failure Recovery Strategy:** Mark the review status as "REQUIRES_HUMAN_AUDIT".
*   **Confidence Scoring:** Based on similarity evaluations.
*   **Explainability Requirements:** Provide justifications for score rating drops.

### 9. Placement Readiness Agent
*   **Input Validation:** Input metrics must be present.
*   **Output Validation:** Output must conform to `readiness_score.json`.
*   **Retry Policy:** No retries. Runs calculations locally.
*   **Failure Recovery Strategy:** Output last saved score from database.
*   **Confidence Scoring:** Static $100\%$ confidence.
*   **Explainability Requirements:** List the sub-scores used in calculations.

---

## SECTION 7 — Capstone Demo Dataset (`CAPSTONE_DEMO_DATASET`)

This dataset is designed for a 5-minute capstone demonstration. It features realistic records that highlights score deltas, gaps, and simulations.

```
       +-----------------------------------------------------------------+
       |                      Target Job Description                     |
       |  - Title: Cloud Backend Engineer                                |
       |  - Mandatory: Node.js, Express, MySQL, Docker                   |
       |  - Preferred Cert: AWS Cloud Practitioner                       |
       +-----------------------------------------------------------------+
          /                        |                   \
         /                         |                    \
        v                          v                     v
 [ Student 1: Ananya ]    [ Student 2: Rohan ]      [ Student 3: Priya ]
  - CGPA: 9.1              - CGPA: 7.2               - CGPA: 8.2
  - Skills: Node, MySQL    - Skills: AWS, Docker     - Skills: Python
  - Certs: None            - Certs: AWS Pract.       - Certs: None
  - Gaps: Docker           - Gaps: Node, MySQL       - Gaps: Node, MySQL, Docker
  - Match: 80%             - Match: 68%              - Match: 30%
  - Readiness: 78          - Readiness: 65           - Readiness: 45
```

### 7.1. Recruiter Profile
*   **Company Name:** CloudScale Technologies
*   **Hiring Manager:** Marcus (Cloud Lead)

### 7.2. Job Description
*   **Role Title:** Cloud Backend Engineer
*   **Mandatory Skills:** `["Node.js", "Express", "MySQL", "Docker"]`
*   **Preferred Certifications:** `["AWS Cloud Practitioner"]`
*   **Minimum CGPA:** $7.5$

### 7.3. Student Profiles

#### Student 1: Ananya (The Strong Coder lacking Cloud)
*   **CGPA:** $9.1$
*   **Skills:** `["JavaScript", "Node.js", "Express", "MySQL", "Git"]`
*   **Projects:**
    *   *Title:* "Restful Bookstore API" (Complexity: 8)
*   **Certifications:** `[]` (None)
*   **Initial Match Score:** $80\%$ (Lacks Docker)
*   **Initial Readiness Score:** $78$
*   **What-If Simulation:**
    *   *Prompt:* "What if Ananya earns AWS Cloud Practitioner and learns Docker?"
    *   *Simulated Match Score:* $98\%$
    *   *Simulated Readiness Score:* $88$ (+10 points)

#### Student 2: Rohan (The Cloud Enthusiast lacking Backend Core)
*   **CGPA:** $7.2$ (Below JD threshold of 7.5)
*   **Skills:** `["AWS", "Docker", "Linux", "Python"]`
*   **Projects:**
    *   *Title:* "Containerized DevOps Flow" (Complexity: 7)
*   **Certifications:** `[{"name": "AWS Cloud Practitioner", "issuer": "AWS"}]`
*   **Initial Match Score:** $68\%$ (Lacks Node.js and MySQL; CGPA is below threshold)
*   **Initial Readiness Score:** $65$
*   **What-If Simulation:**
    *   *Prompt:* "What if Rohan learns Node.js and completes a database project?"
    *   *Simulated Match Score:* $88\%$ (CGPA remains below threshold, which acts as a penalty)
    *   *Simulated Readiness Score:* $79$ (+14 points)

#### Student 3: Priya (The Transitioning Student)
*   **CGPA:** $8.2$
*   **Skills:** `["Python", "HTML", "CSS"]`
*   **Projects:**
    *   *Title:* "Static Personal Portfolio" (Complexity: 3)
*   **Certifications:** `[]`
*   **Initial Match Score:** $30\%$ (Lacks almost all core backend competencies)
*   **Initial Readiness Score:** $45$
*   **What-If Simulation:**
    *   *Prompt:* "What if Priya learns Node.js?"
    *   *Simulated Match Score:* $55\%$
    *   *Simulated Readiness Score:* $56$ (+11 points)

---

## SECTION 8 — Payload Examples

### 8.1. ReadinessHistory Sample Entry
```json
{
  "student_id": "3b2e3f89-8d19-482a-9e12-32b0129e9282",
  "date": "2026-06-20",
  "readiness_score": 78,
  "readiness_breakdown": {
    "technical": 85,
    "projects": 80,
    "communication": 78,
    "interview": 70,
    "certifications": 0
  }
}
```

### 8.2. Upgraded Simulation Output Response
```json
{
  "student_id": "3b2e3f89-8d19-482a-9e12-32b0129e9282",
  "target_job_id": "1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b",
  "original_match_score": 80.0,
  "simulated_match_score": 98.0,
  "original_readiness_score": 78,
  "simulated_readiness_score": 88,
  "explanation": "Match score increased by 18% as Docker completes your containerization skills. Readiness score rose by 10 points due to AWS Cloud Practitioner Tier 2 certification credit."
}
```
