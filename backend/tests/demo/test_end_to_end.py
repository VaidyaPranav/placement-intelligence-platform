from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

# Ensure backend package and repo root are importable when running from tests/demo
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parents[1]
REPO_ROOT = SCRIPT_DIR.parents[2]
for path in (BACKEND_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.agents.company_agent.agent import extract_hiring_requirements
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput
from backend.app.agents.student_agent.agent import extract_student_profile
from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.ranking_agent.agent import rank_student_against_job


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
RESUME_FILE = Path(__file__).resolve().parent.parent / "resume.pdf"
JOB_DESCRIPTION_FILE = Path(__file__).resolve().parent / "job_description.txt"


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(data, "model_dump"):
        data = data.model_dump(mode="json")
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def load_resume_text(path: Path) -> str:
    print("[STEP 1] Loading Resume")
    if not path.exists():
        raise FileNotFoundError(f"Missing resume file: {path}")

    reader = PdfReader(str(path))
    pages = len(reader.pages)
    resume_text = "".join(
        (page.extract_text() or "") + "\n" for page in reader.pages
    )

    print("- PDF Loaded")
    print(f"- Pages Count: {pages}")
    print(f"- Characters Extracted: {len(resume_text)}")

    if len(resume_text.strip()) < 100:
        raise ValueError("Resume text extraction produced less than 100 characters.")

    return resume_text


def load_job_description(path: Path) -> str:
    print("[STEP 3] Loading Job Description")
    if not path.exists():
        raise FileNotFoundError(f"Missing job description file: {path}")

    text = path.read_text(encoding="utf-8")
    print("- JOB DESCRIPTION LOADED")
    print(f"- Character Count: {len(text)}")

    if len(text.strip()) < 50:
        raise ValueError("Job description must be at least 50 characters.")

    return text


def build_student_profile(resume_text: str) -> dict:
    print("[STEP 2] Running Student Intelligence Agent")
    student_profile = extract_student_profile(student_id=str(uuid4()), resume_text=resume_text)

    print("- STUDENT PROFILE GENERATED")
    print(f"- Name: {student_profile.name}")
    print(f"- Department: {student_profile.department}")
    print(f"- CGPA: {student_profile.cgpa}")
    print(f"- Skills Count: {len(student_profile.skills)}")
    print(f"- Projects Count: {len(student_profile.projects)}")
    print(f"- Certifications Count: {len(student_profile.certifications)}")

    write_json(OUTPUT_DIR / "student_profile.json", student_profile.model_dump())
    return student_profile


def build_hiring_requirements(job_description: str) -> CompanyIntelligenceOutput:
    print("[STEP 4] Running Company Intelligence Agent")
    hiring_requirements = extract_hiring_requirements(job_id=str(uuid4()), raw_text=job_description)

    print("- HIRING REQUIREMENTS GENERATED")
    print(f"- Role Title: {hiring_requirements.role_title}")
    print(f"- Experience Level: {hiring_requirements.experience_level}")
    print(f"- Required Skills: {hiring_requirements.required_skills}")
    print(f"- Preferred Skills: {hiring_requirements.preferred_skills}")
    print(f"- Minimum CGPA: {hiring_requirements.minimum_cgpa}")

    write_json(OUTPUT_DIR / "hiring_requirements.json", hiring_requirements.model_dump())
    return hiring_requirements


def ensure_valid_ranking_inputs(
    student_profile, hiring_requirements
) -> tuple[StudentProfile, CompanyIntelligenceOutput]:
    print("[STEP 5] Validating Ranking Agent inputs")
    print(f"type(student_profile): {type(student_profile)}")
    print(f"type(hiring_requirements): {type(hiring_requirements)}")

    if isinstance(student_profile, dict):
        student_profile = StudentProfile.model_validate(student_profile)
        print("- Reconstructed student_profile as StudentProfile from dict")

    if isinstance(hiring_requirements, dict):
        hiring_requirements = CompanyIntelligenceOutput.model_validate(hiring_requirements)
        print("- Reconstructed hiring_requirements as CompanyIntelligenceOutput from dict")

    if not isinstance(student_profile, StudentProfile):
        raise ValueError(
            "student_profile must be a valid StudentProfile instance before ranking. "
            f"Found type: {type(student_profile).__name__}"
        )

    if not isinstance(hiring_requirements, CompanyIntelligenceOutput):
        raise ValueError(
            "hiring_requirements must be a valid CompanyIntelligenceOutput instance before ranking. "
            f"Found type: {type(hiring_requirements).__name__}"
        )

    print(f"- Student ID: {student_profile.student_id}")
    print(f"- Job ID: {hiring_requirements.job_id}")

    return student_profile, hiring_requirements


def build_match_result(student_profile, hiring_requirements) -> dict:
    student_profile, hiring_requirements = ensure_valid_ranking_inputs(
        student_profile, hiring_requirements
    )

    print("[STEP 5] Running Ranking Agent")
    # Enforce deterministic mode for end-to-end pipeline run
    from backend.app.agents.ranking_agent import agent as ranking_agent_mod
    ranking_agent_mod.USE_LLM_ENRICHMENT = False
    print("- Configured Ranking Agent in deterministic mode (USE_LLM_ENRICHMENT = False)")

    match_result = rank_student_against_job(student_profile, hiring_requirements)

    print("- MATCH RESULT GENERATED")
    print(f"- Match Score: {match_result.match_score}")
    print(f"- Recommendation: {match_result.recommendation}")
    print(f"- CGPA Eligible: {match_result.cgpa_eligible}")

    write_json(OUTPUT_DIR / "match_result.json", match_result.model_dump())
    return match_result


def print_report(student_profile, hiring_requirements, match_result) -> None:
    print("\n# ==================================================")
    print("PLACEMENT INTELLIGENCE REPORT")
    try:
        print("Student:", student_profile.name)
        print("Role:", hiring_requirements.role_title)
        print("Match Score:", match_result.match_score)
        print("Recommendation:", match_result.recommendation)
        print("CGPA Eligible:", match_result.cgpa_eligible)
        print("Matched Skills:", ", ".join(match_result.matched_skills) if match_result.matched_skills else "None")
        print("Missing Skills:", ", ".join(match_result.missing_skills) if match_result.missing_skills else "None")
        print("Preferred Skills Matched:", ", ".join(match_result.preferred_skills_matched) if match_result.preferred_skills_matched else "None")
        print("Preferred Skills Missing:", ", ".join(match_result.preferred_skills_missing) if match_result.preferred_skills_missing else "None")
        print("Reasoning:", match_result.reasoning)
    except UnicodeEncodeError:
        print("Student:", student_profile.name.encode('ascii', errors='replace').decode('ascii'))
        print("Role:", hiring_requirements.role_title.encode('ascii', errors='replace').decode('ascii'))
        print("Match Score:", match_result.match_score)
        print("Recommendation:", match_result.recommendation)
        print("CGPA Eligible:", match_result.cgpa_eligible)
        print("Matched Skills:", ", ".join(match_result.matched_skills).encode('ascii', errors='replace').decode('ascii') if match_result.matched_skills else "None")
        print("Missing Skills:", ", ".join(match_result.missing_skills).encode('ascii', errors='replace').decode('ascii') if match_result.missing_skills else "None")
        print("Preferred Skills Matched:", ", ".join(match_result.preferred_skills_matched).encode('ascii', errors='replace').decode('ascii') if match_result.preferred_skills_matched else "None")
        print("Preferred Skills Missing:", ", ".join(match_result.preferred_skills_missing).encode('ascii', errors='replace').decode('ascii') if match_result.preferred_skills_missing else "None")
        print("Reasoning:", match_result.reasoning.encode('ascii', errors='replace').decode('ascii'))
    print("# ==================================================\n")



def main() -> int:
    start = time.time()
    status = "SUCCESS"
    student_confidence = 0.0
    company_confidence = 0.0
    ranking_confidence = 0.0

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        resume_text = load_resume_text(RESUME_FILE)
        student_profile = build_student_profile(resume_text)
        hiring_requirements = build_hiring_requirements(load_job_description(JOB_DESCRIPTION_FILE))
        match_result = build_match_result(student_profile, hiring_requirements)

        student_confidence = student_profile.overall_confidence
        company_confidence = hiring_requirements.overall_confidence
        ranking_confidence = match_result.overall_confidence

        print_report(student_profile, hiring_requirements, match_result)

    except FileNotFoundError as not_found_err:
        print(f"ERROR: {not_found_err}")
        status = "FAILURE"
    except Exception as exc:
        print(f"ERROR: {exc}")
        status = "FAILURE"

    elapsed = round(time.time() - start, 2)
    print(f"PIPELINE STATUS: {status}")
    print(f"Total Execution Time: {elapsed} seconds")
    print(f"Student Confidence Score: {student_confidence}")
    print(f"Company Confidence Score: {company_confidence}")
    print(f"Ranking Confidence Score: {ranking_confidence}")

    return 0 if status == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
