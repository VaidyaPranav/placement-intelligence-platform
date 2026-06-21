# Core Agent Logic for Interview Agent

from uuid import UUID
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput
from backend.app.agents.ranking_agent.schemas import MatchResult
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport

from .schemas import InterviewPreparationReport, InterviewQuestion, DifficultyEnum
from .prompt import SYSTEM_INSTRUCTION

# Configuration option: when False, Gemini is completely bypassed
USE_LLM_ENRICHMENT = False

# Mapped difficulty levels based on MatchResult recommendation string
DIFFICULTY_MAPPING = {
    "STRONG_MATCH": DifficultyEnum.HARD,
    "GOOD_MATCH": DifficultyEnum.MEDIUM,
    "PARTIAL_MATCH": DifficultyEnum.MEDIUM,
    "WEAK_MATCH": DifficultyEnum.EASY,
    "NOT_ELIGIBLE": DifficultyEnum.EASY,
}

# Technical question library for 13 standard skills
TECHNICAL_TEMPLATES = {
    "React": {
        "question": "What is React reconciliation?",
        "expected_answer_keywords": ["Virtual DOM", "Diffing", "Rendering"],
        "evaluation_rubric": [
            "Explains virtual DOM",
            "Explains reconciliation process",
            "Mentions performance benefits"
        ]
    },
    "Node.js": {
        "question": "What is the difference between blocking and non-blocking I/O?",
        "expected_answer_keywords": ["async", "event loop", "non-blocking", "single-threaded"],
        "evaluation_rubric": [
            "Explains event loop",
            "Explains non-blocking I/O",
            "Compares blocking vs non-blocking behavior"
        ]
    },
    "Express": {
        "question": "What is middleware in Express?",
        "expected_answer_keywords": ["middleware", "request", "response", "next"],
        "evaluation_rubric": [
            "Explains middleware function signature",
            "Explains the next() callback function",
            "Gives examples of common middleware use cases"
        ]
    },
    "MySQL": {
        "question": "What is database normalization?",
        "expected_answer_keywords": ["normalization", "redundancy", "anomaly", "foreign keys"],
        "evaluation_rubric": [
            "Defines database normalization",
            "Explains goal of reducing redundancy",
            "Mentions normal forms like 1NF, 2NF, or 3NF"
        ]
    },
    "MongoDB": {
        "question": "What is the difference between SQL and NoSQL databases?",
        "expected_answer_keywords": ["document", "schema-less", "NoSQL", "BSON"],
        "evaluation_rubric": [
            "Contrasts table-based vs document-based storage",
            "Mentions schema flexibility in NoSQL",
            "Explains scalability differences"
        ]
    },
    "Git": {
        "question": "What is the difference between git merge and git rebase?",
        "expected_answer_keywords": ["merge", "rebase", "history", "commits"],
        "evaluation_rubric": [
            "Defines git merge behavior",
            "Defines git rebase behavior",
            "Compares linear history vs commit tracking"
        ]
    },
    "Docker": {
        "question": "What is the difference between a Docker image and a container?",
        "expected_answer_keywords": ["Image", "Container", "Runtime"],
        "evaluation_rubric": [
            "Defines image",
            "Defines container",
            "Explains runtime relationship"
        ]
    },
    "AWS": {
        "question": "What is EC2 and when would you use it?",
        "expected_answer_keywords": ["EC2", "elastic compute", "virtual server", "cloud instance"],
        "evaluation_rubric": [
            "Defines EC2",
            "Explains use cases for resizable compute capacity",
            "Mentions AWS instance types"
        ]
    },
    "Python": {
        "question": "Explain decorators in Python.",
        "expected_answer_keywords": ["decorator", "wrapper", "function", "higher-order"],
        "evaluation_rubric": [
            "Defines python decorator syntax",
            "Explains modifying function behavior dynamically",
            "Gives higher-order function examples"
        ]
    },
    "TensorFlow": {
        "question": "What is a computational graph in TensorFlow?",
        "expected_answer_keywords": ["graph", "tensor", "execution", "sessions"],
        "evaluation_rubric": [
            "Defines computational graph",
            "Explains dataflow graph representation",
            "Mentions lazy execution or eager execution mode"
        ]
    },
    "PyTorch": {
        "question": "What is autograd in PyTorch?",
        "expected_answer_keywords": ["autograd", "gradients", "backpropagation", "tensor"],
        "evaluation_rubric": [
            "Defines autograd",
            "Explains automatic differentiation",
            "Mentions backpropagation engine for neural network training"
        ]
    },
    "SQL": {
        "question": "Explain the difference between WHERE and HAVING in SQL.",
        "expected_answer_keywords": ["WHERE", "HAVING", "GROUP BY", "aggregate"],
        "evaluation_rubric": [
            "Explains WHERE filters individual rows before grouping",
            "Explains HAVING filters grouped/aggregate results",
            "Shows syntactical examples with GROUP BY"
        ]
    },
    "Kubernetes": {
        "question": "What is a Pod in Kubernetes?",
        "expected_answer_keywords": ["Pod", "container", "cluster", "node"],
        "evaluation_rubric": [
            "Defines a Pod as the smallest deployable unit",
            "Explains shared storage/network resources of containers inside Pods",
            "Discusses Pod lifecycle and node relationship"
        ]
    },
}

# Predefined 5 behavioral questions
BEHAVIORAL_QUESTIONS_DATA = [
    {
        "question": "Tell me about a difficult bug you solved.",
        "skill": "Behavioral",
        "difficulty": DifficultyEnum.MEDIUM,
        "expected_answer_keywords": ["debugging", "problem-solving", "resolution"],
        "evaluation_rubric": [
            "Describes debugging methodology",
            "Explains problem-solving mindset",
            "Explains resolution and verification"
        ]
    },
    {
        "question": "Describe a project that failed and what you learned.",
        "skill": "Behavioral",
        "difficulty": DifficultyEnum.MEDIUM,
        "expected_answer_keywords": ["failure", "learning", "growth"],
        "evaluation_rubric": [
            "Explains project context and failure point",
            "Focuses on self-reflection and learnings",
            "Discusses future prevention steps"
        ]
    },
    {
        "question": "Explain a technical challenge you overcame.",
        "skill": "Behavioral",
        "difficulty": DifficultyEnum.MEDIUM,
        "expected_answer_keywords": ["challenge", "overcome", "persistence"],
        "evaluation_rubric": [
            "Defines technical challenge clearly",
            "Outlines step-by-step resolution",
            "Demonstrates persistence and outcome"
        ]
    },
    {
        "question": "Describe a disagreement within a team.",
        "skill": "Behavioral",
        "difficulty": DifficultyEnum.MEDIUM,
        "expected_answer_keywords": ["conflict", "teamwork", "communication"],
        "evaluation_rubric": [
            "Describes conflict situation professionally",
            "Focuses on constructive communication",
            "Shows collaborative teamwork outcome"
        ]
    },
    {
        "question": "Tell me about a time you learned a new technology quickly.",
        "skill": "Behavioral",
        "difficulty": DifficultyEnum.MEDIUM,
        "expected_answer_keywords": ["learning", "adaptability", "quick"],
        "evaluation_rubric": [
            "Identifies technology and timeline",
            "Explains learning resources/approaches",
            "Shows adaptability and successful implementation"
        ]
    },
]


def build_question_for_skill(skill_name: str, difficulty: DifficultyEnum) -> InterviewQuestion:
    """Lookup recommendation from library or return default fallback."""
    for key, data in TECHNICAL_TEMPLATES.items():
        if key.strip().lower() == skill_name.strip().lower():
            return InterviewQuestion(
                question=data["question"],
                skill=key,
                difficulty=difficulty,
                expected_answer_keywords=data["expected_answer_keywords"],
                evaluation_rubric=data["evaluation_rubric"],
            )

    # Unknown skill fallback
    return InterviewQuestion(
        question=f"Explain the core concepts and best practices of using {skill_name} in software development.",
        skill=skill_name,
        difficulty=difficulty,
        expected_answer_keywords=[skill_name, "Architecture", "Best Practices"],
        evaluation_rubric=[
            "Defines the technology",
            "Explains practical use cases",
            "Discusses best practices"
        ],
    )


def calculate_readiness_score(
    match_score: float,
    missing_required: list[str],
    missing_preferred: list[str],
    matched_required: list[str],
) -> float:
    """Calculate the estimated interview readiness score."""
    score = match_score
    score -= 5.0 * len(missing_required)
    score -= 2.0 * len(missing_preferred)
    score += 3.0 * len(matched_required)
    return max(0.0, min(100.0, round(score, 2)))


def generate_focus_areas(missing_required: list[str], missing_preferred: list[str]) -> list[str]:
    """Generate focus areas based on missing skills."""
    seen = set()
    focus = []

    for s in missing_required:
        key = s.strip().lower()
        if key not in seen and s.strip():
            seen.add(key)
            focus.append(s.strip())

    for s in missing_preferred:
        key = s.strip().lower()
        if len(focus) >= 5:
            break
        if key not in seen and s.strip():
            seen.add(key)
            focus.append(s.strip())

    focus.sort()
    return focus


def generate_prep_summary(
    role_title: str,
    readiness_score: float,
    strong_skills: list[str],
    weak_skills: list[str],
    focus_areas: list[str],
) -> str:
    """Generate preparation summary."""
    if not strong_skills:
        strong_str = "no specific technical skills"
    elif len(strong_skills) == 1:
        strong_str = strong_skills[0]
    else:
        strong_str = ", ".join(strong_skills[:-1]) + f" and {strong_skills[-1]}"

    if not weak_skills:
        weak_str = "no specific technical skills"
    elif len(weak_skills) == 1:
        weak_str = weak_skills[0]
    else:
        weak_str = ", ".join(weak_skills[:-1]) + f" and {weak_skills[-1]}"

    lead_in = f"This interview preparation pack focuses on {role_title} interviews. The readiness score is {readiness_score:.1f}."
    skills_assessment = f"The student demonstrates strong {strong_str} skills but should strengthen {weak_str} knowledge before technical rounds."
    focus_assessment = f"Key focus areas for preparation are {', '.join(focus_areas)}." if focus_areas else "No major focus areas identified."

    return f"{lead_in} {skills_assessment} {focus_assessment}"


def generate_deterministic_report(
    student_profile: StudentProfile,
    hiring_requirements: CompanyIntelligenceOutput,
    match_result: MatchResult,
    skill_gap_report: SkillGapReport,
) -> InterviewPreparationReport:
    """Fallback generator when Gemini is bypassed or fails."""
    student_id = student_profile.student_id
    job_id = hiring_requirements.job_id
    role_title = hiring_requirements.role_title

    student_skills = {s.strip().lower() for s in student_profile.skills}

    matched_required = [s for s in hiring_requirements.required_skills if s.strip().lower() in student_skills]
    matched_preferred = [s for s in hiring_requirements.preferred_skills if s.strip().lower() in student_skills]

    missing_required = match_result.missing_skills
    missing_preferred = match_result.preferred_skills_missing

    readiness_score = calculate_readiness_score(
        match_result.match_score,
        missing_required,
        missing_preferred,
        matched_required,
    )

    rec_str = match_result.recommendation.value if hasattr(match_result.recommendation, "value") else str(match_result.recommendation)
    overall_diff = DIFFICULTY_MAPPING.get(rec_str, DifficultyEnum.MEDIUM)

    focus_areas = generate_focus_areas(missing_required, missing_preferred)

    weak_questions = []
    strong_questions = []

    for s in missing_required:
        weak_questions.append(build_question_for_skill(s, DifficultyEnum.HARD))
    for s in missing_preferred:
        weak_questions.append(build_question_for_skill(s, DifficultyEnum.MEDIUM))

    for s in matched_required:
        strong_questions.append(build_question_for_skill(s, DifficultyEnum.HARD))
    for s in matched_preferred:
        strong_questions.append(build_question_for_skill(s, DifficultyEnum.MEDIUM))

    # priority order combined
    tech_questions = []
    for s in missing_required:
        tech_questions.append(build_question_for_skill(s, DifficultyEnum.HARD))
    for s in matched_required:
        tech_questions.append(build_question_for_skill(s, DifficultyEnum.HARD))
    for s in missing_preferred:
        tech_questions.append(build_question_for_skill(s, DifficultyEnum.MEDIUM))
    for s in matched_preferred:
        tech_questions.append(build_question_for_skill(s, DifficultyEnum.MEDIUM))

    behavioral_questions = [
        InterviewQuestion(
            question=q["question"],
            skill=q["skill"],
            difficulty=q["difficulty"],
            expected_answer_keywords=q["expected_answer_keywords"],
            evaluation_rubric=q["evaluation_rubric"],
        )
        for q in BEHAVIORAL_QUESTIONS_DATA
    ]

    strong_skills = matched_required + matched_preferred
    weak_skills = missing_required + missing_preferred
    prep_summary = generate_prep_summary(role_title, readiness_score, strong_skills, weak_skills, focus_areas)

    return InterviewPreparationReport(
        student_id=student_id,
        job_id=job_id,
        role_title=role_title,
        technical_questions=tech_questions,
        behavioral_questions=behavioral_questions,
        weak_area_questions=weak_questions,
        strong_area_questions=strong_questions,
        focus_areas=focus_areas,
        overall_difficulty=overall_diff,
        estimated_interview_readiness_score=readiness_score,
        overall_confidence=match_result.overall_confidence,
        interview_pack_version="1.0.0",
        generated_from_match_score=match_result.match_score,
        preparation_summary=prep_summary,
    )


def enforce_report_rules(
    report: InterviewPreparationReport,
    student_profile: StudentProfile,
    hiring_requirements: CompanyIntelligenceOutput,
    match_result: MatchResult,
    skill_gap_report: SkillGapReport,
) -> InterviewPreparationReport:
    """Enforces absolute correctness on the parsed LLM report output."""
    student_id = student_profile.student_id
    job_id = hiring_requirements.job_id
    role_title = hiring_requirements.role_title

    student_skills = {s.strip().lower() for s in student_profile.skills}
    matched_required = [s for s in hiring_requirements.required_skills if s.strip().lower() in student_skills]
    matched_preferred = [s for s in hiring_requirements.preferred_skills if s.strip().lower() in student_skills]
    missing_required = match_result.missing_skills
    missing_preferred = match_result.preferred_skills_missing

    report.student_id = student_id
    report.job_id = job_id
    report.role_title = role_title
    report.interview_pack_version = "1.0.0"

    readiness_score = calculate_readiness_score(
        match_result.match_score,
        missing_required,
        missing_preferred,
        matched_required,
    )
    report.estimated_interview_readiness_score = readiness_score

    rec_str = match_result.recommendation.value if hasattr(match_result.recommendation, "value") else str(match_result.recommendation)
    overall_diff = DIFFICULTY_MAPPING.get(rec_str, DifficultyEnum.MEDIUM)
    report.overall_difficulty = overall_diff
    report.generated_from_match_score = match_result.match_score

    focus_areas = generate_focus_areas(missing_required, missing_preferred)
    report.focus_areas = focus_areas

    llm_questions_by_skill = {}
    for q in report.technical_questions + report.weak_area_questions + report.strong_area_questions:
        if q.skill:
            llm_questions_by_skill[q.skill.lower().strip()] = q

    tech_questions = []
    weak_questions = []
    strong_questions = []

    def get_question(skill_name: str, default_diff: DifficultyEnum) -> InterviewQuestion:
        key = skill_name.lower().strip()
        if key in llm_questions_by_skill:
            llm_q = llm_questions_by_skill[key]
            if not llm_q.question:
                llm_q.question = f"Explain the core concepts and best practices of using {skill_name} in software development."
            if not llm_q.expected_answer_keywords:
                llm_q.expected_answer_keywords = [skill_name, "Architecture", "Best Practices"]
            if not llm_q.evaluation_rubric:
                llm_q.evaluation_rubric = [
                    "Defines the technology",
                    "Explains practical use cases",
                    "Discusses best practices"
                ]
            llm_q.skill = skill_name
            llm_q.difficulty = default_diff
            return llm_q
        else:
            return build_question_for_skill(skill_name, default_diff)

    for s in missing_required:
        q = get_question(s, DifficultyEnum.HARD)
        tech_questions.append(q)
        weak_questions.append(q)

    for s in matched_required:
        q = get_question(s, DifficultyEnum.HARD)
        tech_questions.append(q)
        strong_questions.append(q)

    for s in missing_preferred:
        q = get_question(s, DifficultyEnum.MEDIUM)
        tech_questions.append(q)
        weak_questions.append(q)

    for s in matched_preferred:
        q = get_question(s, DifficultyEnum.MEDIUM)
        tech_questions.append(q)
        strong_questions.append(q)

    report.technical_questions = tech_questions
    report.weak_area_questions = weak_questions
    report.strong_area_questions = strong_questions

    report.behavioral_questions = [
        InterviewQuestion(
            question=q["question"],
            skill=q["skill"],
            difficulty=q["difficulty"],
            expected_answer_keywords=q["expected_answer_keywords"],
            evaluation_rubric=q["evaluation_rubric"],
        )
        for q in BEHAVIORAL_QUESTIONS_DATA
    ]

    strong_skills = matched_required + matched_preferred
    weak_skills = missing_required + missing_preferred
    report.preparation_summary = generate_prep_summary(role_title, readiness_score, strong_skills, weak_skills, focus_areas)

    return report


# Google ADK Agent Instantiation
interview_agent = Agent(
    name="interview_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=InterviewPreparationReport,
)


def generate_interview_preparation_report(
    student_profile: StudentProfile,
    hiring_requirements: CompanyIntelligenceOutput,
    match_result: MatchResult,
    skill_gap_report: SkillGapReport,
) -> InterviewPreparationReport:
    """
    Validates input schemas, generates a structured InterviewPreparationReport using Gemini
    (if enabled and reachable), and enforces all readiness score calculations, difficulty mapping,
    and focus area generation. Falls back immediately on API errors.
    """
    if not isinstance(student_profile, StudentProfile):
        raise ValueError("student_profile must be a valid StudentProfile instance.")
    if not isinstance(hiring_requirements, CompanyIntelligenceOutput):
        raise ValueError("hiring_requirements must be a valid CompanyIntelligenceOutput instance.")
    if not isinstance(match_result, MatchResult):
        raise ValueError("match_result must be a valid MatchResult instance.")
    if not isinstance(skill_gap_report, SkillGapReport):
        raise ValueError("skill_gap_report must be a valid SkillGapReport instance.")

    if not USE_LLM_ENRICHMENT:
        return generate_deterministic_report(student_profile, hiring_requirements, match_result, skill_gap_report)

    try:
        runner = InMemoryRunner(agent=interview_agent)
        runner.auto_create_session = True

        current_prompt = (
            f"Student Profile:\n"
            f"skills: {student_profile.skills}\n\n"
            f"Hiring Requirements:\n"
            f"role_title: {hiring_requirements.role_title}\n"
            f"required_skills: {hiring_requirements.required_skills}\n"
            f"preferred_skills: {hiring_requirements.preferred_skills}\n\n"
            f"Match Result:\n"
            f"match_score: {match_result.match_score}\n"
            f"recommendation: {match_result.recommendation}\n"
            f"missing_skills: {match_result.missing_skills}\n"
            f"preferred_skills_missing: {match_result.preferred_skills_missing}\n\n"
            f"Skill Gap Report:\n"
            f"severity: {skill_gap_report.severity}\n"
        )

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        )

        events = runner.run(
            user_id="default_user",
            session_id=f"session_{student_profile.student_id}",
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
            if isinstance(output, InterviewPreparationReport):
                parsed_output = output
            elif isinstance(output, dict):
                parsed_output = InterviewPreparationReport.model_validate(output)
            elif isinstance(output, str):
                parsed_output = InterviewPreparationReport.model_validate_json(output)

            if parsed_output is not None:
                return enforce_report_rules(parsed_output, student_profile, hiring_requirements, match_result, skill_gap_report)

        raise ValueError("Empty or malformed LLM response.")

    except Exception as e:
        print(f"[INTERVIEW AGENT] LLM error: {e}. Falling back to deterministic generator.")
        return generate_deterministic_report(student_profile, hiring_requirements, match_result, skill_gap_report)
