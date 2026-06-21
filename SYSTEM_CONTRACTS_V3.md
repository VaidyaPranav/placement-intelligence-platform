# System Contracts Specification V3: Future-Proof Student Profile
## Placement Intelligence Platform (PIP) — Schema & Contract Upgrades

This document defines the upgraded `StudentProfile` specification, ensuring compatibility with downstream matching, ranking, analytics, and governance agents.

---

## SECTION 1 — Updated StudentProfile Entity Schema

We expand the student profile to capture resume extraction metadata, GitHub analysis placeholders, readiness sub-scores, career preference states, and detailed explainability links.

### 1.1. StudentProfile Entity
*   **Description:** The complete, structured profile of a student, verified by multiple sources, tracked over time, and used for matching runs.
*   **Required Fields:**
    *   `student_id` (UUIDv4)
    *   `name` (String)
    *   `department` (Enum: `CS`, `IT`, `ECE`, `EE`, `ME`)
    *   `cgpa` (Float, $0.0 \le x \le 10.0$)
    *   `skills` (Array of tech-tags)
    *   `projects` (Array of Project objects)
    *   `certifications` (Array of Certification objects)
    *   `achievements` (Array of Strings)
    *   `internships` (Array of Internship objects)
    *   `resume_text` (String - raw text extracted from the PDF resume)
    *   `resume_confidence` (Float, $0.0 \le x \le 1.0$)
    *   `verified_sources` (Array of Strings, e.g. `["RESUME_PDF", "GITHUB"]`)
    *   `github_analysis` (GitHubAnalysis Object)
    *   `technical_score` (Integer, default 0)
    *   `project_score` (Integer, default 0)
    *   `communication_score` (Integer, default 0)
    *   `interview_score` (Integer, default 0)
    *   `certification_score` (Integer, default 0)
    *   `placement_status` (Enum: `UNPLACED`, `PLACED`, `SNOOZED`, default `UNPLACED`)
    *   `target_role_category` (Enum: `Software Engineering`, `Data & Analytics`, `AI/ML`, `Cloud & DevOps`, default `Software Engineering`)
    *   `profile_version` (String, default `"1.0.0"`)
    *   `overall_confidence` (Float, $0.0 \le x \le 1.0$)
    *   `explainability_section` (ExplainabilitySection Object)
    *   `created_at` (ISO 8601 Datetime String)
    *   `updated_at` (ISO 8601 Datetime String)
*   **Optional Fields:**
    *   `github_url` (URI)
    *   `portfolio_url` (URI)
    *   `linkedin_url` (URI)

### 1.2. Nested Sub-Objects

#### Project
*   `title` (String)
*   `complexity_score` (Integer, $1 \le x \le 10$)

#### Certification
*   `name` (String)
*   `issuer` (String)

#### Internship
*   `company` (String)
*   `role` (String)
*   `duration_months` (Integer, $\ge 1$)

#### GitHubAnalysis
*   `repo_count` (Integer, default 0)
*   `languages` (Array of Strings, default `[]`)
*   `verification_status` (Enum: `UNVERIFIED`, `VERIFIED`, `PARTIAL`, default `UNVERIFIED`)

#### ExplainabilitySection
*   `name_evidence` (String)
*   `department_evidence` (String)
*   `cgpa_evidence` (String)
*   `skill_evidence` (Array of objects containing `skill_tag`: String, `evidence_sentence`: String)
*   `project_evidence` (Array of objects containing `project_title`: String, `evidence_sentence`: String)
*   `certification_evidence` (Array of objects containing `certification_name`: String, `evidence_sentence`: String)
*   `internship_evidence` (Array of objects containing `internship_company`: String, `evidence_sentence`: String)

---

## SECTION 2 — Updated JSON Schema (`student_profile.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StudentProfile",
  "type": "object",
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "name": { "type": "string" },
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
    },
    "resume_text": { "type": "string" },
    "resume_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "verified_sources": { "type": "array", "items": { "type": "string" } },
    "github_analysis": {
      "type": "object",
      "properties": {
        "repo_count": { "type": "integer", "default": 0 },
        "languages": { "type": "array", "items": { "type": "string" } },
        "verification_status": { "type": "string", "enum": ["UNVERIFIED", "VERIFIED", "PARTIAL"], "default": "UNVERIFIED" }
      },
      "required": ["repo_count", "languages", "verification_status"]
    },
    "technical_score": { "type": "integer", "minimum": 0, "maximum": 100, "default": 0 },
    "project_score": { "type": "integer", "minimum": 0, "maximum": 100, "default": 0 },
    "communication_score": { "type": "integer", "minimum": 0, "maximum": 100, "default": 0 },
    "interview_score": { "type": "integer", "minimum": 0, "maximum": 100, "default": 0 },
    "certification_score": { "type": "integer", "minimum": 0, "maximum": 100, "default": 0 },
    "placement_status": { "type": "string", "enum": ["UNPLACED", "PLACED", "SNOOZED"], "default": "UNPLACED" },
    "target_role_category": { "type": "string", "enum": ["Software Engineering", "Data & Analytics", "AI/ML", "Cloud & DevOps"], "default": "Software Engineering" },
    "profile_version": { "type": "string", "default": "1.0.0" },
    "overall_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "github_url": { "type": "string", "format": "uri" },
    "portfolio_url": { "type": "string", "format": "uri" },
    "linkedin_url": { "type": "string", "format": "uri" },
    "explainability_section": {
      "type": "object",
      "properties": {
        "name_evidence": { "type": "string" },
        "department_evidence": { "type": "string" },
        "cgpa_evidence": { "type": "string" },
        "skill_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "skill_tag": { "type": "string" },
              "evidence_sentence": { "type": "string" }
            },
            "required": ["skill_tag", "evidence_sentence"]
          }
        },
        "project_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "project_title": { "type": "string" },
              "evidence_sentence": { "type": "string" }
            },
            "required": ["project_title", "evidence_sentence"]
          }
        },
        "certification_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "certification_name": { "type": "string" },
              "evidence_sentence": { "type": "string" }
            },
            "required": ["certification_name", "evidence_sentence"]
          }
        },
        "internship_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "internship_company": { "type": "string" },
              "evidence_sentence": { "type": "string" }
            },
            "required": ["internship_company", "evidence_sentence"]
          }
        }
      },
      "required": ["name_evidence", "department_evidence", "cgpa_evidence", "skill_evidence", "project_evidence", "certification_evidence", "internship_evidence"]
    }
  },
  "required": [
    "student_id", "name", "department", "cgpa", "skills", "projects", "certifications", "achievements", "internships",
    "resume_text", "resume_confidence", "verified_sources", "github_analysis", "technical_score", "project_score",
    "communication_score", "interview_score", "certification_score", "placement_status", "target_role_category",
    "profile_version", "overall_confidence", "explainability_section", "created_at", "updated_at"
  ]
}
```

---

## SECTION 3 — Updated Student Intelligence Agent Contract

*   **Purpose:** Convert raw, unstructured resume text into the enhanced, future-proof `StudentProfile` JSON.
*   **Input Schema:** `{"student_id": "UUIDv4", "resume_text": "String"}`
*   **Output Schema:** `student_profile.json`
*   **Input Validation Rules:**
    1.  `student_id` must match exact UUIDv4 format (regex check).
    2.  `resume_text` length must be $\ge 100$ characters.
*   **Output Validation Rules:**
    1.  All default values (`technical_score`, `project_score`, `communication_score`, `interview_score`, `certification_score` = 0) must be populated.
    2.  `github_analysis` block must be created with `"verification_status": "UNVERIFIED"`.
    3.  `overall_confidence` and sub-confidences must range between $0.0$ and $1.0$.
    4.  All explainability evidence array objects must contain mapping references.

---

## SECTION 4 — Future Compatibility Review

We evaluate the sufficiency of the enhanced `StudentProfile` to support downstream agent logic:

1.  **Ranking Agent:**
    *   *Sufficiency:* **High**. Downstream ranking requires matching technical skills, CGPA limits, certifications, and project complexity. All matching parameters are exposed.
2.  **Skill Gap Agent:**
    *   *Sufficiency:* **High**. Set-difference calculation utilizes the `skills` array. Gaps in project complexity are checked against `projects`.
3.  **Placement Readiness Agent:**
    *   *Sufficiency:* **High**. The readiness agent gathers `technical_score`, `project_score`, `communication_score`, `interview_score`, and `certification_score` directly from this profile. By providing these fields inside the profile, the readiness agent can write back updated metrics without altering the DB schema.
4.  **Career Roadmap Agent:**
    *   *Sufficiency:* **High**. Uses `target_role_category` and the gaps to map out the study path.
5.  **Recruiter Analytics Agent:**
    *   *Sufficiency:* **High**. The added `placement_status` field ensures recruiters only see unplaced students. The readiness scores allow filtering and rendering distribution graphs.
6.  **Governance Agent:**
    *   *Sufficiency:* **High**. The `verified_sources` list and timestamps (`created_at`, `updated_at`) allow auditing of manual and automatic modifications.
7.  **Evaluation Agent:**
    *   *Sufficiency:* **High**. The raw `resume_text` is saved directly inside the profile. This allows the evaluator LLM-as-a-judge to compare the parsed output fields directly against the original resume text without having to re-fetch the PDF blob from Storage.

No additional fields are required; this design is robust for complete system implementation.
