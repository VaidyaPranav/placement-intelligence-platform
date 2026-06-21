# Skill: Interview Agent

Generates role-specific, structured interview preparation reports containing technical questions (with detailed rubrics), behavioral questions, focus areas, and preparation summaries.

## Description

The agent analyzes the candidate's matched and missing required/preferred skills to prioritize technical questions, maps the matching score recommendation to an overall interview difficulty level, and calculates an interview readiness score with specific adjustments.

## Inputs
- `student_profile` (`StudentProfile`)
- `hiring_requirements` (`CompanyIntelligenceOutput`)
- `match_result` (`MatchResult`)
- `skill_gap_report` (`SkillGapReport`)

## Outputs
- `InterviewPreparationReport`: A structured object containing:
  - `student_id` (UUID)
  - `job_id` (UUID)
  - `role_title` (str)
  - `technical_questions` (List of `InterviewQuestion`)
  - `behavioral_questions` (List of `InterviewQuestion`)
  - `weak_area_questions` (List of `InterviewQuestion`)
  - `strong_area_questions` (List of `InterviewQuestion`)
  - `focus_areas` (List of str)
  - `overall_difficulty` (DifficultyEnum)
  - `estimated_interview_readiness_score` (float)
  - `overall_confidence` (float)
  - `interview_pack_version` (str)
  - `generated_from_match_score` (float)
  - `preparation_summary` (str)

## Mapping & Scoring Rules

### Overall Difficulty Mapping
- `STRONG_MATCH` $\rightarrow$ `HARD`
- `GOOD_MATCH` $\rightarrow$ `MEDIUM`
- `PARTIAL_MATCH` $\rightarrow$ `MEDIUM`
- `WEAK_MATCH` $\rightarrow$ `EASY`
- `NOT_ELIGIBLE` $\rightarrow$ `EASY`

### Readiness Score Calculation
- Start from `MatchResult.match_score`.
- Subtract $5.0$ for each missing required skill.
- Subtract $2.0$ for each missing preferred skill.
- Add $3.0$ for each matched required skill.
- Clamp the score between $0.0$ and $100.0$.

### Focus Areas Rules
1. Include all missing required skills.
2. Include missing preferred skills if the total count of focus areas is less than 5.
3. Remove duplicates.
4. Sort alphabetically.

### Question Prioritization Order
Technical questions must be sorted in this order:
1. Missing Required Skills
2. Matched Required Skills
3. Missing Preferred Skills
4. Matched Preferred Skills
