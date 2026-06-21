# ADK Skill: Technical Skill Gap Analysis and Recommendations
## Metadata
*   **Name:** `skill_gap_analysis`
*   **Description:** Compares a student's technical skills against job requirements to calculate gaps, score severity, and map structured learning recommendations.

## Inputs
*   `student_profile` (StudentProfile): The structured student profile.
*   `hiring_requirements` (CompanyIntelligenceOutput): The structured job hiring requirements.
*   `match_result` (MatchResult): The calculated match result.

## Outputs
*   Conforms to `SkillGapReport` schema:
    *   `student_id` (UUID)
    *   `job_id` (UUID)
    *   `gap_score` (Float, 0.0 to 100.0)
    *   `missing_required_skills` (List of Strings)
    *   `missing_preferred_skills` (List of Strings)
    *   `severity` (Enum: LOW, MEDIUM, HIGH, CRITICAL)
    *   `recommendations` (List of SkillRecommendation)
    *   `overall_confidence` (Float)

## Execution Guarantees
1.  **Deterministic Gap Scoring:**
    *   Formula: $\text{GapScore} = (\text{Ratio of Missing Required Skills} \times 70.0) + (\text{Ratio of Missing Preferred Skills} \times 30.0)$
    *   Severity mapping:
        *   $0 \le \text{GapScore} \le 20$: `LOW`
        *   $21 \le \text{GapScore} \le 50$: `MEDIUM`
        *   $51 \le \text{GapScore} \le 80$: `HIGH`
        *   $81 \le \text{GapScore} \le 100$: `CRITICAL`
2.  **Completeness Guarantee:** Generates exactly one `SkillRecommendation` for each missing required and preferred skill.
3.  **Local Fallback Library:** Automatically maps structured recommendation roadmaps using a local library.
