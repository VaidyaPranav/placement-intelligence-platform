# ADK Skill: Student to Job Match Ranking
## Metadata
*   **Name:** `student_job_ranking`
*   **Description:** Evaluates a student profile against job requirements to produce a match score and recommendation.

## Inputs
*   `student_profile` (StudentProfile): The structured student profile.
*   `hiring_requirements` (CompanyIntelligenceOutput): The structured job hiring requirements.

## Outputs
*   Conforms to `MatchResult` schema:
    *   `student_id` (UUID)
    *   `job_id` (UUID)
    *   `match_score` (Float, 0.0 to 100.0)
    *   `matched_skills` (List of Strings)
    *   `missing_skills` (List of Strings)
    *   `preferred_skills_matched` (List of Strings)
    *   `preferred_skills_missing` (List of Strings)
    *   `cgpa_eligible` (Boolean)
    *   `recommendation` (Enum: STRONG_MATCH, GOOD_MATCH, PARTIAL_MATCH, WEAK_MATCH, NOT_ELIGIBLE)
    *   `reasoning` (String)
    *   `overall_confidence` (Float)

## Execution Guarantees
1.  **Deterministic Scoring Engine:**
    *   Required Skills Weight: $70\%$
    *   Preferred Skills Weight: $20\%$
    *   CGPA Eligibility Weight: $10\%$
    *   Final Score: $\text{RequiredSkillScore} \times 0.70 + \text{PreferredSkillScore} \times 0.20 + \text{CGPAPresenceScore} \times 0.10$
2.  **CGPA Boundary check:** Forces recommendation to `NOT_ELIGIBLE` if the student's CGPA is less than the job's minimum requirement.
3.  **Local Fallback:** Runs the deterministic engine locally if the Gemini API fails or times out.
