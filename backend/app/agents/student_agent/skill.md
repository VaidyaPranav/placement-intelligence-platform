# ADK Skill: Student Resume Parsing and Profiling
## Metadata
*   **Name:** `student_resume_profiling`
*   **Description:** Parses unstructured student resume text to extract academic majors, skills, projects, certifications, internships, achievements, and explainability evidence.

## Inputs
*   `resume_text` (String): The plain text extracted from a PDF resume. Minimum length: 100 characters.
*   `student_id` (String): A valid UUIDv4 identifier.

## Outputs
*   Conforms to `StudentProfile` schema:
    *   `student_id` (UUID)
    *   `name` (String)
    *   `department` (Enum: CS, IT, ECE, EE, ME)
    *   `cgpa` (Float, 0.0 to 10.0)
    *   `skills` (List of Strings)
    *   `projects` (List of Projects containing title and complexity_score)
    *   `certifications` (List of Certifications containing name and issuer)
    *   `achievements` (List of Strings)
    *   `internships` (List of Internships containing company, role, duration_months)
    *   `resume_text` (String)
    *   `resume_confidence` (Float)
    *   `verified_sources` (List of Strings)
    *   `github_analysis` (Object)
    *   `technical_score` (Integer)
    *   `project_score` (Integer)
    *   `communication_score` (Integer)
    *   `interview_score` (Integer)
    *   `certification_score` (Integer)
    *   `placement_status` (String)
    *   `target_role_category` (String)
    *   `profile_version` (String)
    *   `overall_confidence` (Float)
    *   `explainability_section` (Object)
    *   `created_at` (Datetime)
    *   `updated_at` (Datetime)
    *   `github_url` (Optional String)
    *   `portfolio_url` (Optional String)
    *   `linkedin_url` (Optional String)

## Execution Guarantees
1.  **Normalization:** Standardizes typical variations of technical skills (e.g. ReactJS -> React, NodeJS -> Node.js, Tensor Flow -> TensorFlow).
2.  **Taxonomy & Complexity:** Assigns project complexity scores clamped strictly to standard institutional categories (CRUD: 3-4, Full Stack: 5-7, Cloud: 7-8, AI/ML: 8-10).
3.  **Department Mapping:** Classifies major names into standard Enums.
4.  **Self-Correction:** Implements a 3-attempt LLM repair cycle before falling back to local regex matching.
