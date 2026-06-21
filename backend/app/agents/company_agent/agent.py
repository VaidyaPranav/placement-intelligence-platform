# Core Agent Logic for Company Intelligence Agent

import re
from uuid import UUID
import backend.app.config as config
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from .schemas import CompanyIntelligenceOutput, ExplainabilitySection, SkillEvidence, ExperienceLevelEnum
from .prompt import SYSTEM_INSTRUCTION


# 1. Skill Normalization Layer
def normalize_skill(skill: str) -> str:
    """Normalize common tech skill keywords to their official standard names."""
    mapping = {
        "reactjs": "React",
        "react.js": "React",
        "node": "Node.js",
        "nodejs": "Node.js",
        "my sql": "MySQL",
        "mysql": "MySQL",
        "aws cloud practitioner": "AWS Cloud Practitioner",
        "aws certified cloud practitioner": "AWS Cloud Practitioner",
    }
    cleaned = skill.strip().lower()
    return mapping.get(cleaned, skill.strip())


# 2. Role Taxonomy Mapping
def get_role_category(role_title: str) -> str:
    """Map a parsed role title to one of the four main system categories."""
    title_lower = role_title.lower()
    if any(re.search(rf"\b{re.escape(w)}\b", title_lower) for w in ["backend", "frontend", "full stack", "fullstack", "developer", "software engineer", "programmer", "development"]):
        return "Software Engineering"
    elif any(re.search(rf"\b{re.escape(w)}\b", title_lower) for w in ["data analyst", "business analyst", "data engineer", "analytics", "bi developer", "analyst"]):
        return "Data & Analytics"
    elif any(re.search(rf"\b{re.escape(w)}\b", title_lower) for w in ["machine learning", "ml", "ai", "artificial intelligence", "nlp", "specialist"]):
        return "AI/ML"
    elif any(re.search(rf"\b{re.escape(w)}\b", title_lower) for w in ["cloud", "devops", "sysops", "sre", "systems"]):
        return "Cloud & DevOps"
    return "Software Engineering"  # Default fallback category


# 3. Regex Fallback Parser (Failure Recovery Strategy)
def fallback_regex_parse(job_id: str, raw_text: str, error_msg: str) -> CompanyIntelligenceOutput:
    """Fallback extraction using regular expressions when the LLM repeatedly fails."""
    # Extrapolate title
    title_match = re.search(r"(?:title|position|role|job title):\s*([^\n]+)", raw_text, re.IGNORECASE)
    role_title = title_match.group(1).strip() if title_match else "Unknown Role"

    # Identify skills present in text
    test_skills = ["Python", "JavaScript", "React", "Node.js", "MySQL", "AWS", "Docker", "Kubernetes", "Tableau", "PyTorch", "CSS", "HTML"]
    found_skills = []
    for skill in test_skills:
        if re.search(rf"\b{re.escape(skill)}\b", raw_text, re.IGNORECASE):
            found_skills.append(normalize_skill(skill))

    # Guess experience level
    experience_level = ExperienceLevelEnum.ENTRY_LEVEL
    if re.search(r"\bintern\b", raw_text, re.IGNORECASE):
        experience_level = ExperienceLevelEnum.INTERNSHIP
    elif re.search(r"\bjunior\b", raw_text, re.IGNORECASE):
        experience_level = ExperienceLevelEnum.JUNIOR
    elif re.search(r"\bmid\b", raw_text, re.IGNORECASE):
        experience_level = ExperienceLevelEnum.MID_LEVEL
    elif re.search(r"\bsenior\b", raw_text, re.IGNORECASE):
        experience_level = ExperienceLevelEnum.SENIOR

    # Guess GPA
    gpa_match = re.search(r"\b(?:gpa|cgpa)\s*(?:of|minimum|min)?\s*([0-9](?:\.[0-9])?)\b", raw_text, re.IGNORECASE)
    minimum_cgpa = float(gpa_match.group(1)) if gpa_match else 0.0

    evidence_skills = [SkillEvidence(skill_tag=s, evidence_sentence="Found in text.") for s in found_skills]

    explainability = ExplainabilitySection(
        role_evidence="Parsed via regex title matcher.",
        skill_evidence=evidence_skills,
        cgpa_evidence="CGPA match found via regex parser." if minimum_cgpa > 0.0 else "CGPA not found by regex."
    )

    return CompanyIntelligenceOutput(
        job_id=UUID(job_id),
        role_title=role_title,
        role_category=get_role_category(role_title),
        experience_level=experience_level,
        required_skills=found_skills[:3] if found_skills else ["Software Development"],
        preferred_skills=found_skills[3:],
        soft_skills=["Communication"],
        minimum_cgpa=minimum_cgpa,
        extraction_method="fallback",
        overall_confidence=0.1,
        skill_confidence=0.1,
        role_confidence=0.1,
        cgpa_confidence=0.1,
        explainability_section=explainability
    )


# 4. Google ADK Agent Instantiation
company_agent = Agent(
    name="company_intelligence_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=CompanyIntelligenceOutput
)


def extract_hiring_requirements(job_id: str, raw_text: str) -> CompanyIntelligenceOutput:
    """
    Validates inputs, executes Gemini extraction with a 3-attempt repair loop,
    and falls back to a regex parser if all attempts fail or Gemini is unavailable.
    """
    # Validation 1: Length check
    if len(raw_text.strip()) < 50:
        raise ValueError("Job description text must be at least 50 characters.")

    # Validation 2: UUID format check
    try:
        validated_uuid = UUID(job_id)
    except ValueError:
        raise ValueError("job_id must be a valid UUIDv4 string.")

    # Check configuration to bypass Gemini entirely
    if not getattr(config, "USE_LLM_ENRICHMENT", True):
        print("[COMPANY AGENT]\nGemini unavailable.\nUsing deterministic fallback.")
        result = fallback_regex_parse(job_id, raw_text, "LLM enrichment disabled.")
        result.extraction_method = "fallback"
        result.overall_confidence = 0.1
        return result

    try:
        # Instantiate runner and set auto_create_session on instance
        runner = InMemoryRunner(agent=company_agent)
        runner.auto_create_session = True
        
        current_prompt = f"Extract requirements for job_id: {job_id} from this description:\n\n{raw_text}"
        last_error = ""

        # Attempt 3-step repair loop
        for attempt in range(1, 4):
            try:
                # Prepare message in correct types.Content format
                user_message = types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=current_prompt)]
                )
                
                # Execute Gemini via ADK runner (returns generator of events)
                events = runner.run(
                    user_id="default_user",
                    session_id=f"session_{job_id}",
                    new_message=user_message
                )
                
                output = None
                content_payload = None
                event_type = None

                print("\n========== ADK EVENTS ==========")

                for idx, event in enumerate(events):
                    print(f"\nEVENT #{idx}")
                    print("TYPE:", type(event))

                    try:
                        print("DIR:", dir(event))
                    except Exception:
                        pass

                    try:
                        print("DICT:", event.__dict__)
                    except Exception:
                        pass

                    if hasattr(event, "output") and event.output is not None:
                        print("FOUND event.output")
                        print(event.output)
                        output = event.output
                        event_type = type(event)

                    if hasattr(event, "content") and event.content is not None:
                        print("FOUND event.content")
                        print(event.content)
                        content_payload = event.content
                        if event_type is None:
                            event_type = type(event)

                print("\n========== END EVENTS ==========\n")

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
                    # Add diagnostic logging
                    print(f"[DIAGNOSTIC LOG] Event type: {event_type}")
                    print(f"[DIAGNOSTIC LOG] Output type: {type(output)}")
                    print(f"[DIAGNOSTIC LOG] Raw output payload: {output}")

                    # Robust multi-type parsing
                    parsed_output = None
                    if isinstance(output, CompanyIntelligenceOutput):
                        parsed_output = output
                    elif isinstance(output, dict):
                        parsed_output = CompanyIntelligenceOutput.model_validate(output)
                    elif isinstance(output, str):
                        parsed_output = CompanyIntelligenceOutput.model_validate_json(output)
                    
                    if parsed_output is not None:
                        # Normalization Layer on successful parse
                        parsed_output.required_skills = [normalize_skill(s) for s in parsed_output.required_skills]
                        parsed_output.preferred_skills = [normalize_skill(s) for s in parsed_output.preferred_skills]
                        parsed_output.role_category = get_role_category(parsed_output.role_title)
                        parsed_output.extraction_method = "llm"
                        return parsed_output
                
                raise ValueError("Output did not match expected Pydantic model schema or could not be parsed.")
            except Exception as e:
                last_error = str(e)
                # Formulate repair prompt for next attempt
                current_prompt = (
                    f"CORRECTION REQUIRED (Attempt {attempt+1}): The previous attempt failed validation with error: {last_error}.\n"
                    f"Please ensure you return a JSON object strictly matching the schema parameters.\n"
                    f"Original job description:\n{raw_text}"
                )

        raise ValueError(f"All 3 repair attempts failed. Last error: {last_error}")

    except Exception as e:
        print("[COMPANY AGENT]")
        print("Gemini unavailable.")
        print("Using deterministic fallback.")

        if not getattr(config, "ENABLE_AUTOMATIC_FALLBACK", True):
            raise e

        result = fallback_regex_parse(job_id, raw_text, str(e))
        result.extraction_method = "fallback"
        result.overall_confidence = 0.1
        return result
