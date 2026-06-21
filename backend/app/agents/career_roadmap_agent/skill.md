# Skill: Career Roadmap Agent

Converts a `SkillGapReport` and `StudentProfile` into a structured, multi-week learning roadmap to help students close placement gaps.

## Description

The agent maps the severity of placement gaps to a 1–4 week roadmap, schedules tasks prioritizing high-priority skills, and constructs a summary details statement that summarizes the program.

## Inputs
- `student_profile` (`StudentProfile`): Profile containing student info.
- `skill_gap_report` (`SkillGapReport`): The report containing missing skills and recommendations.

## Outputs
- `CareerRoadmap`: A structured object containing:
  - `student_id` (UUID)
  - `total_weeks` (int)
  - `roadmap_weeks` (List of `RoadmapWeek` / `RoadmapTask`)
  - `expected_match_score_improvement` (float)
  - `overall_confidence` (float)
  - `roadmap_version` (str)
  - `generated_from_severity` (SeverityEnum)
  - `roadmap_summary` (str)

## Mapping Rules
- `LOW` severity -> 1 week
- `MEDIUM` severity -> 2 weeks
- `HIGH` severity -> 3 weeks
- `CRITICAL` severity -> 4 weeks

## Scheduling Rules
- `HIGH` priority tasks scheduled in earlier weeks.
- Items are distributed evenly across the weeks.
