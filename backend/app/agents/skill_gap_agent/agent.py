# Core Agent Logic for Skill Gap Agent

from uuid import UUID
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput
from backend.app.agents.ranking_agent.schemas import MatchResult

from .schemas import SkillGapReport, SkillRecommendation, PriorityEnum, SeverityEnum
from .prompt import SYSTEM_INSTRUCTION

# Configuration option: when False, Gemini is completely bypassed
USE_LLM_ENRICHMENT = False

# Hardcoded library of standard skill recommendations
RECOMMENDATION_LIBRARY = {
    "React": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Build a React project using hooks, routing, and API integration.",
        "estimated_improvement_score": 10.0,
    },
    "Node.js": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Create REST APIs using Express and connect them to a database.",
        "estimated_improvement_score": 10.0,
    },
    "Docker": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Learn Docker fundamentals and containerize one existing project.",
        "estimated_improvement_score": 12.0,
    },
    "AWS": {
        "priority": PriorityEnum.MEDIUM,
        "recommendation": "Deploy a full-stack application on AWS EC2 and S3.",
        "estimated_improvement_score": 8.0,
    },
    "Kubernetes": {
        "priority": PriorityEnum.MEDIUM,
        "recommendation": "Learn Kubernetes deployments, services, and scaling concepts.",
        "estimated_improvement_score": 7.0,
    },
    "PyTorch": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Build and train an end-to-end deep learning project.",
        "estimated_improvement_score": 10.0,
    },
    "SQL": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Practice joins, indexing, normalization, and query optimization.",
        "estimated_improvement_score": 8.0,
    },
    "MySQL": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Practice SQL queries, joins, indexes, and database normalization.",
        "estimated_improvement_score": 8.0,
    },
    "Git": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Learn Git workflows, branching, merging, and pull request mechanics.",
        "estimated_improvement_score": 5.0,
    },
    "MongoDB": {
        "priority": PriorityEnum.MEDIUM,
        "recommendation": "Learn NoSQL database schema design and CRUD operations in MongoDB.",
        "estimated_improvement_score": 6.0,
    },
    "Python": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Learn Python fundamentals, data structures, and object-oriented programming.",
        "estimated_improvement_score": 8.0,
    },
    "TensorFlow": {
        "priority": PriorityEnum.HIGH,
        "recommendation": "Build deep learning models using TensorFlow Keras APIs.",
        "estimated_improvement_score": 10.0,
    },
}


# 1. Deterministic Scoring Engine Functions
def calculate_gap_score(
    missing_required: list[str],
    total_required: list[str],
    missing_preferred: list[str],
    total_preferred: list[str],
) -> tuple[float, SeverityEnum]:
    """Calculate the gap score and map it to a SeverityEnum level."""
    req_ratio = (len(missing_required) / len(total_required)) if total_required else 0.0
    pref_ratio = (len(missing_preferred) / len(total_preferred)) if total_preferred else 0.0

    gap_score = (req_ratio * 70.0) + (pref_ratio * 30.0)
    gap_score = max(0.0, min(100.0, round(gap_score, 2)))

    if gap_score <= 20.0:
        severity = SeverityEnum.LOW
    elif gap_score <= 50.0:
        severity = SeverityEnum.MEDIUM
    elif gap_score <= 80.0:
        severity = SeverityEnum.HIGH
    else:
        severity = SeverityEnum.CRITICAL

    return gap_score, severity


# 2. Local recommendation engine lookup/fallback generator
def build_recommendation(skill_name: str, is_required: bool = False) -> SkillRecommendation:
    """Lookup recommendation from library or return default fallback."""
    for key, data in RECOMMENDATION_LIBRARY.items():
        if key.strip().lower() == skill_name.strip().lower():
            return SkillRecommendation(
                skill=key,
                priority=data["priority"],
                recommendation=data["recommendation"],
                estimated_improvement_score=data["estimated_improvement_score"],
            )

    # Unknown skill fallback
    default_priority = PriorityEnum.HIGH if is_required else PriorityEnum.LOW
    return SkillRecommendation(
        skill=skill_name,
        priority=default_priority,
        recommendation=f"Learn the fundamentals of {skill_name} and build one practical project.",
        estimated_improvement_score=5.0,
    )


# 3. Deterministic Local Fallback Report Generator
def fallback_deterministic_report(
    student_id: UUID,
    job_id: UUID,
    missing_required: list[str],
    total_required: list[str],
    missing_preferred: list[str],
    total_preferred: list[str],
) -> SkillGapReport:
    """Fallback generator when Gemini is bypassed or fails."""
    gap_score, severity = calculate_gap_score(missing_required, total_required, missing_preferred, total_preferred)

    # Build recommendations for every missing skill
    recommendations = []
    for skill in missing_required:
        recommendations.append(build_recommendation(skill, is_required=True))
    for skill in missing_preferred:
        recommendations.append(build_recommendation(skill, is_required=False))

    return SkillGapReport(
        student_id=student_id,
        job_id=job_id,
        gap_score=gap_score,
        missing_required_skills=missing_required,
        missing_preferred_skills=missing_preferred,
        severity=severity,
        recommendations=recommendations,
        overall_confidence=0.1,
    )


# 4. Google ADK Agent Instantiation
skill_gap_agent = Agent(
    name="skill_gap_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=SkillGapReport,
)


def generate_skill_gap_report(
    student_profile: StudentProfile,
    hiring_requirements: CompanyIntelligenceOutput,
    match_result: MatchResult,
) -> SkillGapReport:
    """
    Validates input schemas, generates a structured SkillGapReport using Gemini
    (if enabled and reachable), and enforces absolute deterministic scoring accuracy
    and recommendation completeness. Falls back immediately on API errors.
    """
    if not isinstance(student_profile, StudentProfile):
        raise ValueError("student_profile must be a valid StudentProfile instance.")
    if not isinstance(hiring_requirements, CompanyIntelligenceOutput):
        raise ValueError("hiring_requirements must be a valid CompanyIntelligenceOutput instance.")
    if not isinstance(match_result, MatchResult):
        raise ValueError("match_result must be a valid MatchResult instance.")

    student_id = student_profile.student_id
    job_id = hiring_requirements.job_id

    # Compute expected details deterministically
    expected_score, expected_severity = calculate_gap_score(
        match_result.missing_skills,
        hiring_requirements.required_skills,
        match_result.preferred_skills_missing,
        hiring_requirements.preferred_skills,
    )

    # If LLM enrichment is disabled, run local engine immediately
    if not USE_LLM_ENRICHMENT:
        print("[SKILL GAP AGENT] USE_LLM_ENRICHMENT is False. Bypassing Gemini entirely.")
        return fallback_deterministic_report(
            student_id,
            job_id,
            match_result.missing_skills,
            hiring_requirements.required_skills,
            match_result.preferred_skills_missing,
            hiring_requirements.preferred_skills,
        )

    # Attempt LLM run once
    try:
        runner = InMemoryRunner(agent=skill_gap_agent)
        runner.auto_create_session = True

        current_prompt = (
            f"Student Profile:\n"
            f"student_id: {student_id}\n"
            f"skills: {student_profile.skills}\n\n"
            f"Hiring Requirements:\n"
            f"job_id: {job_id}\n"
            f"required_skills: {hiring_requirements.required_skills}\n"
            f"preferred_skills: {hiring_requirements.preferred_skills}\n\n"
            f"Match Result:\n"
            f"missing_skills: {match_result.missing_skills}\n"
            f"preferred_skills_missing: {match_result.preferred_skills_missing}\n"
        )

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        )

        events = runner.run(
            user_id="default_user",
            session_id=f"session_{student_id}_{job_id}",
            new_message=user_message,
        )

        output = None
        content_payload = None

        for event in events:
            if hasattr(event, "output") and event.output is not None:
                output = event.output
            if hasattr(event, "content") and event.content is not None:
                content_payload = event.content

        if output is None and content_payload is not None:
            if hasattr(content_payload, "parts"):
                text_parts = []
                for part in getattr(content_payload, "parts", []):
                    if hasattr(part, "text") and part.text is not None:
                        text_parts.append(part.text)
                output = "".join(text_parts).strip() if text_parts else content_payload
            else:
                output = content_payload

        if output is not None:
            parsed_output = None
            if isinstance(output, SkillGapReport):
                parsed_output = output
            elif isinstance(output, dict):
                parsed_output = SkillGapReport.model_validate(output)
            elif isinstance(output, str):
                parsed_output = SkillGapReport.model_validate_json(output)

            if parsed_output is not None:
                # Enforce absolute mathematical correctness on top of LLM output
                parsed_output.student_id = student_id
                parsed_output.job_id = job_id
                parsed_output.gap_score = expected_score
                parsed_output.missing_required_skills = match_result.missing_skills
                parsed_output.missing_preferred_skills = match_result.preferred_skills_missing
                parsed_output.severity = expected_severity

                # Verify all missing skills have recommendations
                missing_set = set(match_result.missing_skills + match_result.preferred_skills_missing)
                rec_set = {r.skill for r in parsed_output.recommendations}
                
                # If recommendations are missing, fill them in using local library
                for skill in missing_set:
                    if skill not in rec_set:
                        is_req = skill in match_result.missing_skills
                        parsed_output.recommendations.append(build_recommendation(skill, is_required=is_req))

                return parsed_output

        raise ValueError("Empty or malformed LLM response.")

    except Exception as e:
        print(f"[SKILL GAP AGENT] LLM unavailable or error occurred: {e}. Executing deterministic local engine immediately.")
        return fallback_deterministic_report(
            student_id,
            job_id,
            match_result.missing_skills,
            hiring_requirements.required_skills,
            match_result.preferred_skills_missing,
            hiring_requirements.preferred_skills,
        )

