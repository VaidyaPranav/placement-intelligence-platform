# Core Agent Logic for Student Intelligence Agent

import re
from uuid import UUID
import backend.app.config as config
import concurrent.futures
from datetime import datetime, timezone
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from .schemas import (
    StudentProfile,
    Project,
    Certification,
    Internship,
    GitHubAnalysis,
    ExplainabilitySection,
    SkillEvidence,
    ProjectEvidence,
    CertificationEvidence,
    InternshipEvidence,
    DepartmentEnum,
    PlacementStatusEnum,
    TargetRoleCategoryEnum,
)
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
        "tensor flow": "TensorFlow",
        "tensorflow": "TensorFlow",
        "powerbi": "Power BI",
        "power bi": "Power BI",
    }
    cleaned = skill.strip().lower()
    return mapping.get(cleaned, skill.strip())


# 2. Project Complexity Adjustment Layer
def adjust_project_complexity(title: str, score: int) -> int:
    """Clamp complexity score to designated brackets depending on keyword content."""
    title_lower = title.lower()
    if "crud" in title_lower:
        if not (3 <= score <= 4):
            return 4
    elif any(w in title_lower for w in ["full stack", "fullstack", "web app", "django", "flask", "springboot"]):
        if not (5 <= score <= 7):
            return 6
    elif any(w in title_lower for w in ["cloud", "aws", "gcp", "azure", "terraform", "devops", "kubernetes", "docker", "ci/cd", "pipeline"]):
        if not (7 <= score <= 8):
            return 8
    elif any(w in title_lower for w in ["ai", "ml", "machine learning", "deep learning", "neural", "pytorch", "tensorflow", "nlp", "vision", "resnet", "cnn", "lstm"]):
        if not (8 <= score <= 10):
            return 9
    return max(1, min(10, score))


# 3. Department Mapping Layer
def map_department(dept_str: str) -> DepartmentEnum:
    """Map raw major/department text to the standard institutional Enum values."""
    cleaned = dept_str.strip().upper()
    if any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in ["COMPUTER SCIENCE", "CSE", "CS"]):
        return DepartmentEnum.CS
    if any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in ["INFORMATION TECHNOLOGY", "IT"]):
        return DepartmentEnum.IT
    if any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in ["ELECTRONICS", "ECE", "COMMUNICATION"]):
        return DepartmentEnum.ECE
    if any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in ["ELECTRICAL", "EE"]):
        return DepartmentEnum.EE
    if any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in ["MECHANICAL", "ME"]):
        return DepartmentEnum.ME
    return DepartmentEnum.CS


# 4. Target Role Category Prediction
def predict_target_role_category(skills: list[str], projects: list[Project]) -> TargetRoleCategoryEnum:
    """Infer the primary student career path based on extracted skills and project titles."""
    skills_lower = [s.lower() for s in skills]
    project_titles_lower = [p.title.lower() for p in projects]

    # Check AI/ML (more specific keywords first)
    ai_specific = ["pytorch", "tensorflow", "keras", "machine learning", "deep learning", "nlp", "computer vision", "opencv", "resnet", "neural network"]
    if any(any(k in s for k in ai_specific) for s in skills_lower) or any(any(k in p for k in ai_specific) for p in project_titles_lower):
        return TargetRoleCategoryEnum.AI_ML

    # Check Cloud & DevOps
    cloud_specific = ["aws", "azure", "gcp", "terraform", "kubernetes", "devops", "jenkins", "ansible", "ci/cd"]
    if any(any(k in s for k in cloud_specific) for s in skills_lower) or any(any(k in p for k in cloud_specific) for p in project_titles_lower):
        return TargetRoleCategoryEnum.CLOUD_DEVOPS

    # Check Data & Analytics (using word boundaries or specific checks to avoid MySQL matching sql)
    data_specific = ["tableau", "power bi", "powerbi", "excel", "data analyst", "analytics", "dashboard"]
    has_sql_role = any(s == "sql" for s in skills_lower) or any(re.search(r"\bsql\b", p) for p in project_titles_lower)
    if has_sql_role or any(any(k in s for k in data_specific) for s in skills_lower) or any(any(k in p for k in data_specific) for p in project_titles_lower):
        return TargetRoleCategoryEnum.DATA_ANALYTICS

    # Check general AI/ML fallback if Python is used with some generic ML term (like 'ai' or 'ml' as word)
    ai_general = ["ai", "ml"]
    if any(any(re.search(r"\b" + re.escape(k) + r"\b", s) for k in ai_general) for s in skills_lower) or any(any(re.search(r"\b" + re.escape(k) + r"\b", p) for k in ai_general) for p in project_titles_lower):
        return TargetRoleCategoryEnum.AI_ML

    return TargetRoleCategoryEnum.SOFTWARE_ENGINEERING


# 5. Regex Fallback Parser (Failure Recovery Strategy)
def fallback_regex_parse(student_id: str, raw_text: str, error_msg: str) -> StudentProfile:
    """Fallback extraction using regular expressions when the LLM repeatedly fails."""
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    name = "Unknown Student"
    if lines:
        first_line = lines[0]
        if not any(marker in first_line.lower() for marker in ["resume", "email", "github", "linkedin", "phone"]):
            name = first_line

    # Mapped Department
    department = map_department(raw_text)

    # GPA / CGPA Extraction
    cgpa = 0.0
    cgpa_match = re.search(r"\b(?:cgpa|gpa|grade)\s*(?:of|is|:)?\s*([0-9](?:\.[0-9]+)?)\b", raw_text, re.IGNORECASE)
    if cgpa_match:
        try:
            val = float(cgpa_match.group(1))
            if 0.0 <= val <= 10.0:
                cgpa = val
        except ValueError:
            pass

    # URL Parsers
    github_url = None
    portfolio_url = None
    linkedin_url = None

    github_match = re.search(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+", raw_text, re.IGNORECASE)
    if github_match:
        github_url = github_match.group(0)

    linkedin_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", raw_text, re.IGNORECASE)
    if linkedin_match:
        linkedin_url = linkedin_match.group(0)

    portfolio_match = re.search(r"https?://(?:www\.)?(?!github|linkedin)[a-zA-Z0-9_-]+\.[a-z]{2,}(?:/[a-zA-Z0-9_-]+)*", raw_text, re.IGNORECASE)
    if portfolio_match:
        portfolio_url = portfolio_match.group(0)

    # Skill extraction (scan for matching terms, including variants)
    test_skills = ["Python", "Java", "C++", "JavaScript", "React", "ReactJS", "React.js", "Node", "NodeJS", "Node.js", "MySQL", "My SQL", "AWS", "Docker", "Kubernetes", "Tableau", "TensorFlow", "Tensor Flow", "PyTorch", "Excel", "Power BI", "PowerBI", "HTML", "CSS", "Git"]
    found_skills = []
    for skill in test_skills:
        if re.search(rf"\b{re.escape(skill)}\b", raw_text, re.IGNORECASE):
            found_skills.append(normalize_skill(skill))
    if not found_skills:
        found_skills = ["Software Development"]

    found_skills = list(dict.fromkeys(found_skills))

    # Project extraction
    projects = []
    project_matches = re.findall(r"(?:project|projects):\s*\n*(.*?)(?:\n\n|\n[A-Z]|$)", raw_text, re.IGNORECASE | re.DOTALL)
    if project_matches:
        proj_lines = [line.strip("- *•") for line in project_matches[0].split("\n") if line.strip()]
        for line in proj_lines[:3]:
            parts = line.split(":")
            title = parts[0].strip() if parts else "Sample Project"
            if len(title) > 50:
                title = title[:47] + "..."
            projects.append(Project(title=title, complexity_score=adjust_project_complexity(title, 5)))
    if not projects:
        projects = [Project(title="System Project", complexity_score=5)]

    # Certification extraction
    certifications = []
    cert_matches = re.findall(r"(?:certification|certifications|courses):\s*\n*(.*?)(?:\n\n|\n[A-Z]|$)", raw_text, re.IGNORECASE | re.DOTALL)
    if cert_matches:
        cert_lines = [line.strip("- *•") for line in cert_matches[0].split("\n") if line.strip()]
        for line in cert_lines[:3]:
            parts = line.split(":")
            c_name = parts[0].strip() if parts else "Professional Certificate"
            c_issuer = parts[1].strip() if len(parts) > 1 else "External Provider"
            certifications.append(Certification(name=c_name, issuer=c_issuer))

    # Internship extraction
    internships = []
    intern_matches = re.findall(r"(?:internship|internships|experience):\s*\n*(.*?)(?:\n\n|\n[A-Z]|$)", raw_text, re.IGNORECASE | re.DOTALL)
    if intern_matches:
        intern_lines = [line.strip("- *•") for line in intern_matches[0].split("\n") if line.strip()]
        for line in intern_lines[:3]:
            parts = line.split("at")
            role = parts[0].strip() if parts else "Intern"
            company = parts[1].strip() if len(parts) > 1 else "Enterprise"
            duration = 3
            dur_match = re.search(r"(\d+)\s*month", line, re.IGNORECASE)
            if dur_match:
                duration = int(dur_match.group(1))
            internships.append(Internship(company=company, role=role, duration_months=duration))

    # Evidence mapping
    skill_evidence = [SkillEvidence(skill_tag=s, evidence_sentence="Found in skills section.") for s in found_skills]
    project_evidence = [ProjectEvidence(project_title=p.title, evidence_sentence="Found in projects section.") for p in projects]
    certification_evidence = [CertificationEvidence(certification_name=c.name, evidence_sentence="Found in certifications section.") for c in certifications]
    internship_evidence = [InternshipEvidence(internship_company=i.company, evidence_sentence="Found in internships section.") for i in internships]

    explainability = ExplainabilitySection(
        name_evidence="Extracted via top line name parser.",
        department_evidence="Department mapped via major keyword matching.",
        cgpa_evidence="CGPA parsed using numeric search." if cgpa > 0.0 else "CGPA not specified.",
        skill_evidence=skill_evidence,
        project_evidence=project_evidence,
        certification_evidence=certification_evidence,
        internship_evidence=internship_evidence
    )

    now = datetime.now(timezone.utc)

    return StudentProfile(
        student_id=UUID(student_id),
        name=name,
        department=department,
        cgpa=cgpa,
        skills=found_skills,
        projects=projects,
        certifications=certifications,
        achievements=[],
        internships=internships,
        resume_text=raw_text,
        resume_confidence=0.1,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(
            repo_count=0,
            languages=[],
            verification_status="UNVERIFIED"
        ),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=predict_target_role_category(found_skills, projects),
        profile_version="1.0.0",
        extraction_method="fallback",
        overall_confidence=0.1,
        explainability_section=explainability,
        created_at=now,
        updated_at=now,
        github_url=github_url,
        portfolio_url=portfolio_url,
        linkedin_url=linkedin_url
    )



# 6. Google ADK Agent Instantiation
student_agent = Agent(
    name="student_intelligence_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=StudentProfile
)


def extract_student_profile(student_id: str, resume_text: str) -> StudentProfile:
    """
    Validates inputs, executes Gemini extraction with a 3-attempt repair loop,
    and falls back to a regex parser if all attempts fail or Gemini is unavailable.
    """
    # Validation 1: Length check
    if len(resume_text.strip()) < 100:
        raise ValueError("Resume text must be at least 100 characters.")

    # Validation 2: UUID format check
    try:
        validated_uuid = UUID(student_id)
    except ValueError:
        raise ValueError("student_id must be a valid UUIDv4 string.")

    # Check configuration to bypass Gemini entirely
    if not getattr(config, "USE_LLM_ENRICHMENT", True):
        print("[STUDENT AGENT]\nGemini unavailable.\nUsing deterministic fallback.")
        profile = fallback_regex_parse(student_id, resume_text, "LLM enrichment disabled.")
        profile.extraction_method = "fallback"
        profile.overall_confidence = 0.1
        return profile

    try:
        # Instantiate runner and set auto_create_session
        runner = InMemoryRunner(agent=student_agent)
        runner.auto_create_session = True

        current_prompt = f"Extract student profile for student_id: {student_id} from this resume:\n\n{resume_text}"
        last_error = ""

        # Attempt 3-step repair loop
        for attempt in range(1, 4):
            try:
                # Prepare message
                user_message = types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=current_prompt)]
                )

                # Execute Gemini via ADK runner with a timeout to avoid indefinite blocking.
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as exc:
                    future = exc.submit(
                        runner.run,
                        user_id="default_user",
                        session_id=f"session_{student_id}",
                        new_message=user_message,
                    )
                    try:
                        events = future.result(timeout=30)
                    except concurrent.futures.TimeoutError:
                        future.cancel()
                        raise RuntimeError("Gemini ADK call timed out after 30s")

                output = None
                content_payload = None
                event_type = None

                print(f"\n========== ADK EVENTS (ATTEMPT {attempt}) ==========")
                for idx, event in enumerate(events):
                    print(f"EVENT #{idx} TYPE: {type(event)}")

                    if hasattr(event, "output") and event.output is not None:
                        output = event.output
                        event_type = type(event)

                    if hasattr(event, "content") and event.content is not None:
                        content_payload = event.content
                        if event_type is None:
                            event_type = type(event)

                print("========== END EVENTS ==========\n")

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
                    # Diagnostics
                    print(f"[DIAGNOSTIC] Output type: {type(output)}")

                    # Parsing
                    parsed_output = None
                    if isinstance(output, StudentProfile):
                        parsed_output = output
                    elif isinstance(output, dict):
                        parsed_output = StudentProfile.model_validate(output)
                    elif isinstance(output, str):
                        parsed_output = StudentProfile.model_validate_json(output)

                    if parsed_output is not None:
                        # Enforce/Override values to match exactly
                        parsed_output.student_id = validated_uuid
                        parsed_output.resume_text = resume_text

                        # Normalization Layer on skills
                        parsed_output.skills = list(dict.fromkeys([normalize_skill(s) for s in parsed_output.skills]))

                        # Project complexity scoring adjustments
                        for proj in parsed_output.projects:
                            proj.complexity_score = adjust_project_complexity(proj.title, proj.complexity_score)

                        # Category prediction
                        parsed_output.target_role_category = predict_target_role_category(
                            parsed_output.skills, parsed_output.projects
                        )

                        # Ensure timestamps are set
                        if not parsed_output.created_at:
                            parsed_output.created_at = datetime.now(timezone.utc)
                        parsed_output.updated_at = datetime.now(timezone.utc)

                        # Defaults check
                        parsed_output.technical_score = 0
                        parsed_output.project_score = 0
                        parsed_output.communication_score = 0
                        parsed_output.interview_score = 0
                        parsed_output.certification_score = 0
                        parsed_output.placement_status = PlacementStatusEnum.UNPLACED
                        parsed_output.github_analysis = GitHubAnalysis(
                            repo_count=0,
                            languages=[],
                            verification_status="UNVERIFIED"
                        )
                        parsed_output.extraction_method = "llm"

                        return parsed_output

                raise ValueError("Output did not match expected Pydantic model schema or could not be parsed.")

            except Exception as e:
                last_error = str(e)
                print(f"[REPAIR LOOP WARNING] Attempt {attempt} failed: {last_error}")
                current_prompt = (
                    f"CORRECTION REQUIRED (Attempt {attempt+1}): The previous attempt failed validation with error: {last_error}.\n"
                    f"Please ensure you return a JSON object strictly matching the schema parameters.\n"
                    f"Original resume text:\n{resume_text}"
                )

        raise ValueError(f"All 3 repair attempts failed. Last error: {last_error}")

    except Exception as e:
        print("[STUDENT AGENT]")
        print("Gemini unavailable.")
        print("Using deterministic fallback.")

        if not getattr(config, "ENABLE_AUTOMATIC_FALLBACK", True):
            raise e

        profile = fallback_regex_parse(student_id, resume_text, str(e))
        profile.extraction_method = "fallback"
        profile.overall_confidence = 0.1
        return profile
