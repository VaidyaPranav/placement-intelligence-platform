# Core Agent Logic for Ranking Agent

from uuid import UUID
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput

from .schemas import MatchResult, RecommendationEnum
from .prompt import SYSTEM_INSTRUCTION

# Configuration option: when False, Gemini is completely bypassed
USE_LLM_ENRICHMENT = False


# 1. Deterministic Scoring Engine Function
def calculate_match_details(
    student_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
    student_cgpa: float,
    minimum_cgpa: float,
) -> tuple[float, list[str], list[str], list[str], list[str], bool]:
    """Calculate match metrics deterministically based on standard institutional rules."""
    stud_skills_set = {s.strip().lower() for s in student_skills}

    matched_req = []
    missing_req = []
    for req in required_skills:
        if req.strip().lower() in stud_skills_set:
            matched_req.append(req)
        else:
            missing_req.append(req)

    matched_pref = []
    missing_pref = []
    for pref in preferred_skills:
        if pref.strip().lower() in stud_skills_set:
            matched_pref.append(pref)
        else:
            missing_pref.append(pref)

    cgpa_eligible = student_cgpa >= minimum_cgpa

    req_score = (len(matched_req) / len(required_skills) * 100.0) if required_skills else 100.0
    pref_score = (len(matched_pref) / len(preferred_skills) * 100.0) if preferred_skills else 100.0
    cgpa_score = 100.0 if cgpa_eligible else 0.0

    match_score = (req_score * 0.70) + (pref_score * 0.20) + (cgpa_score * 0.10)
    match_score = max(0.0, min(100.0, round(match_score, 2)))

    return match_score, matched_req, missing_req, matched_pref, missing_pref, cgpa_eligible


# 2. Recommendation Mapping Function
def get_recommendation(match_score: float, cgpa_eligible: bool) -> RecommendationEnum:
    """Map Match Score or CGPA eligibility to RecommendationEnum category."""
    if not cgpa_eligible:
        return RecommendationEnum.NOT_ELIGIBLE
    if match_score >= 90.0:
        return RecommendationEnum.STRONG_MATCH
    elif match_score >= 75.0:
        return RecommendationEnum.GOOD_MATCH
    elif match_score >= 60.0:
        return RecommendationEnum.PARTIAL_MATCH
    elif match_score >= 40.0:
        return RecommendationEnum.WEAK_MATCH
    else:
        return RecommendationEnum.NOT_ELIGIBLE


# 3. Deterministic Local Fallback Ranking Generator
def fallback_deterministic_rank(
    student_id: UUID,
    job_id: UUID,
    student_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
    student_cgpa: float,
    minimum_cgpa: float,
    reasoning_prefix: str,
) -> MatchResult:
    """Fallback generator when Gemini is unreachable, disabled, or validation fails."""
    score, matched_req, missing_req, matched_pref, missing_pref, cgpa_eligible = calculate_match_details(
        student_skills, required_skills, preferred_skills, student_cgpa, minimum_cgpa
    )
    rec = get_recommendation(score, cgpa_eligible)

    req_score = (len(matched_req) / len(required_skills) * 100.0) if required_skills else 100.0
    pref_score = (len(matched_pref) / len(preferred_skills) * 100.0) if preferred_skills else 100.0
    cgpa_score = 100.0 if cgpa_eligible else 0.0

    reasoning = (
        f"{reasoning_prefix} "
        f"Required skills matched: {len(matched_req)} of {len(required_skills)} ({'100' if not required_skills else int(len(matched_req)/len(required_skills)*100)}%). "
        f"Preferred skills matched: {len(matched_pref)} of {len(preferred_skills)} ({'100' if not preferred_skills else int(len(matched_pref)/len(preferred_skills)*100)}%). "
        f"CGPA is {student_cgpa}, which is {'eligible' if cgpa_eligible else 'not eligible'} (minimum required: {minimum_cgpa})."
    )

    return MatchResult(
        student_id=student_id,
        job_id=job_id,
        match_score=score,
        matched_skills=matched_req,
        missing_skills=missing_req,
        preferred_skills_matched=matched_pref,
        preferred_skills_missing=missing_pref,
        cgpa_eligible=cgpa_eligible,
        recommendation=rec,
        reasoning=reasoning,
        overall_confidence=0.1,
        required_skill_score=round(req_score, 2),
        preferred_skill_score=round(pref_score, 2),
        cgpa_score=round(cgpa_score, 2),
    )


# 4. Google ADK Agent Instantiation
ranking_agent = Agent(
    name="ranking_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=MatchResult,
)


def rank_student_against_job(
    student_profile: StudentProfile, hiring_requirements: CompanyIntelligenceOutput
) -> MatchResult:
    """
    Validates input schemas. If USE_LLM_ENRICHMENT is False, runs the deterministic engine immediately.
    Otherwise, runs Gemini and falls back to deterministic scoring immediately on any API error.
    """
    # Validation 1: Schema Checks
    if not isinstance(student_profile, StudentProfile):
        raise ValueError("student_profile must be a valid StudentProfile instance.")
    if not isinstance(hiring_requirements, CompanyIntelligenceOutput):
        raise ValueError("hiring_requirements must be a valid CompanyIntelligenceOutput instance.")

    student_id = student_profile.student_id
    job_id = hiring_requirements.job_id

    # Compute expected details deterministically to enforce alignment
    expected_score, expected_m_req, expected_ms_req, expected_m_pref, expected_ms_pref, expected_cgpa_el = calculate_match_details(
        student_profile.skills,
        hiring_requirements.required_skills,
        hiring_requirements.preferred_skills,
        student_profile.cgpa,
        hiring_requirements.minimum_cgpa,
    )
    expected_rec = get_recommendation(expected_score, expected_cgpa_el)

    # Fast-path: Run local deterministic logic if enrichment is disabled
    if not USE_LLM_ENRICHMENT:
        print("[RANKING AGENT] USE_LLM_ENRICHMENT is False. Bypassing Gemini entirely.")
        return fallback_deterministic_rank(
            student_id,
            job_id,
            student_profile.skills,
            hiring_requirements.required_skills,
            hiring_requirements.preferred_skills,
            student_profile.cgpa,
            hiring_requirements.minimum_cgpa,
            "Local deterministic scoring (LLM enrichment disabled).",
        )

    # Attempt LLM run once
    try:
        runner = InMemoryRunner(agent=ranking_agent)
        runner.auto_create_session = True

        current_prompt = (
            f"Compare Student Profile:\n"
            f"student_id: {student_id}\n"
            f"cgpa: {student_profile.cgpa}\n"
            f"skills: {student_profile.skills}\n\n"
            f"Against Hiring Requirements:\n"
            f"job_id: {job_id}\n"
            f"required_skills: {hiring_requirements.required_skills}\n"
            f"preferred_skills: {hiring_requirements.preferred_skills}\n"
            f"minimum_cgpa: {hiring_requirements.minimum_cgpa}\n"
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
            if isinstance(output, MatchResult):
                parsed_output = output
            elif isinstance(output, dict):
                parsed_output = MatchResult.model_validate(output)
            elif isinstance(output, str):
                parsed_output = MatchResult.model_validate_json(output)

            if parsed_output is not None:
                # Enforce absolute mathematical correctness on top of LLM output
                parsed_output.student_id = student_id
                parsed_output.job_id = job_id
                parsed_output.match_score = expected_score
                parsed_output.matched_skills = expected_m_req
                parsed_output.missing_skills = expected_ms_req
                parsed_output.preferred_skills_matched = expected_m_pref
                parsed_output.preferred_skills_missing = expected_ms_pref
                parsed_output.cgpa_eligible = expected_cgpa_el
                parsed_output.recommendation = expected_rec
                
                expected_req_score = (len(expected_m_req) / len(hiring_requirements.required_skills) * 100.0) if hiring_requirements.required_skills else 100.0
                expected_pref_score = (len(expected_m_pref) / len(hiring_requirements.preferred_skills) * 100.0) if hiring_requirements.preferred_skills else 100.0
                expected_cgpa_score = 100.0 if expected_cgpa_el else 0.0
                
                parsed_output.required_skill_score = round(expected_req_score, 2)
                parsed_output.preferred_skill_score = round(expected_pref_score, 2)
                parsed_output.cgpa_score = round(expected_cgpa_score, 2)
                return parsed_output

        raise ValueError("Empty or malformed LLM response.")

    except Exception as e:
        # Fall back instantly on 503, high demand, timeouts, or any exception
        print(f"[RANKING AGENT] LLM unavailable or error occurred: {e}. Falling back to deterministic matching immediately.")
        return fallback_deterministic_rank(
            student_id,
            job_id,
            student_profile.skills,
            hiring_requirements.required_skills,
            hiring_requirements.preferred_skills,
            student_profile.cgpa,
            hiring_requirements.minimum_cgpa,
            f"LLM Enrichment failed ({e}). Fallback to local scoring.",
        )

