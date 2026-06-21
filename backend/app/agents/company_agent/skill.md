# ADK Skill: Job Description Requirement Extraction
## Metadata
*   **Name:** `job_description_extraction`
*   **Description:** Parses raw, unstructured job description text to extract structured roles, categories, skills, and CGPA metrics.

## Inputs
*   `raw_text` (String): The job description. Minimum length: 50 characters.
*   `job_id` (String): A valid UUIDv4 identifier.

## Outputs
*   Conforms to `CompanyIntelligenceOutput` schema:
    *   `job_id` (UUID)
    *   `role_title` (String)
    *   `role_category` (String)
    *   `experience_level` (String)
    *   `required_skills` (List of Strings)
    *   `preferred_skills` (List of Strings)
    *   `soft_skills` (List of Strings)
    *   `minimum_cgpa` (Float)
    *   `overall_confidence` (Float)
    *   `explainability_section` (Object)

## Execution Guarantees
1.  **Normalization:** Standardizes typical variations of technical skills (e.g. ReactJS -> React).
2.  **Taxonomy Alignment:** Categorizes role titles into standard college career paths.
3.  **Self-Correction:** Implements a 3-attempt LLM repair cycle before falling back to local regex matching.
