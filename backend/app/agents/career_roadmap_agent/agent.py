# Core Agent Logic for Career Roadmap Agent

from uuid import UUID
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from backend.app.agents.student_agent.schemas import StudentProfile
from backend.app.agents.skill_gap_agent.schemas import SkillGapReport, PriorityEnum, SeverityEnum
from .schemas import CareerRoadmap, RoadmapWeek, RoadmapTask, DifficultyEnum
from .prompt import SYSTEM_INSTRUCTION

# Configuration option: when False, Gemini is completely bypassed
USE_LLM_ENRICHMENT = False

# Severity to weeks mapping
SEVERITY_WEEKS_MAPPING = {
    SeverityEnum.LOW: 1,
    SeverityEnum.MEDIUM: 2,
    SeverityEnum.HIGH: 3,
    SeverityEnum.CRITICAL: 4,
}

# Local template library for 12 standard skills
ROADMAP_TEMPLATES = {
    "React": {
        "title": "Master React Components & State",
        "description": "Build interactive UI components, manage state with hooks (useState, useEffect), and handle user events.",
        "estimated_hours": 8.0,
        "difficulty": DifficultyEnum.INTERMEDIATE,
    },
    "Node.js": {
        "title": "Build RESTful APIs with Node.js & Express",
        "description": "Create server-side applications, route HTTP requests, handle middleware, and manage async operations.",
        "estimated_hours": 10.0,
        "difficulty": DifficultyEnum.INTERMEDIATE,
    },
    "Docker": {
        "title": "Containerize Applications with Docker",
        "description": "Write Dockerfiles, build container images, run multi-container applications using Docker Compose.",
        "estimated_hours": 6.0,
        "difficulty": DifficultyEnum.BEGINNER,
    },
    "AWS": {
        "title": "Deploy Applications on AWS",
        "description": "Configure EC2 instances, manage files in S3 buckets, and set up basic IAM security rules.",
        "estimated_hours": 8.0,
        "difficulty": DifficultyEnum.INTERMEDIATE,
    },
    "Kubernetes": {
        "title": "Orchestrate Containers with Kubernetes",
        "description": "Define Pods, Deployments, Services, and manage application configuration and scaling.",
        "estimated_hours": 10.0,
        "difficulty": DifficultyEnum.ADVANCED,
    },
    "PyTorch": {
        "title": "Deep Learning Model Development with PyTorch",
        "description": "Understand tensors, construct neural networks using nn.Module, and write custom training loops.",
        "estimated_hours": 12.0,
        "difficulty": DifficultyEnum.ADVANCED,
    },
    "SQL": {
        "title": "Relational Database Querying & Joins",
        "description": "Write complex SELECT statements, perform table joins, filter data, and design database schemas.",
        "estimated_hours": 6.0,
        "difficulty": DifficultyEnum.BEGINNER,
    },
    "MySQL": {
        "title": "Database Administration & MySQL Queries",
        "description": "Configure MySQL databases, perform CRUD operations, use indexes, and write optimized queries.",
        "estimated_hours": 6.0,
        "difficulty": DifficultyEnum.BEGINNER,
    },
    "Git": {
        "title": "Version Control & Git Collaboration",
        "description": "Initialize repositories, commit changes, manage branches, merge code, and resolve conflicts.",
        "estimated_hours": 4.0,
        "difficulty": DifficultyEnum.BEGINNER,
    },
    "MongoDB": {
        "title": "NoSQL Schema Design & MongoDB",
        "description": "Perform CRUD operations, write aggregation pipelines, and design document schemas.",
        "estimated_hours": 8.0,
        "difficulty": DifficultyEnum.INTERMEDIATE,
    },
    "Python": {
        "title": "Python Programming Fundamentals",
        "description": "Learn syntax, data structures (lists, dicts), file I/O, and object-oriented programming in Python.",
        "estimated_hours": 8.0,
        "difficulty": DifficultyEnum.BEGINNER,
    },
    "TensorFlow": {
        "title": "Deep Learning Models with TensorFlow",
        "description": "Construct and compile sequential/functional models, use Keras layers, and train on datasets.",
        "estimated_hours": 10.0,
        "difficulty": DifficultyEnum.ADVANCED,
    },
}


def build_task_for_skill(skill_name: str, week_number: int) -> RoadmapTask:
    """Lookup recommendation from library or return default fallback."""
    for key, data in ROADMAP_TEMPLATES.items():
        if key.strip().lower() == skill_name.strip().lower():
            return RoadmapTask(
                week_number=week_number,
                skill=key,
                title=data["title"],
                description=data["description"],
                estimated_hours=data["estimated_hours"],
                difficulty=data["difficulty"],
            )

    # Unknown skill fallback
    return RoadmapTask(
        week_number=week_number,
        skill=skill_name,
        title=f"Learn {skill_name} Fundamentals",
        description=f"Study the core concepts of {skill_name} and complete practical exercises.",
        estimated_hours=6.0,
        difficulty=DifficultyEnum.BEGINNER,
    )


def generate_summary(
    severity: SeverityEnum,
    total_weeks: int,
    recommendations: list,
    expected_improvement: float,
) -> str:
    """Generate a severity-specific roadmap summary containing key details."""
    lead_in = ""
    if severity == SeverityEnum.LOW:
        lead_in = f"This {total_weeks}-week roadmap focuses on strengthening a small number of placement skills."
    elif severity == SeverityEnum.MEDIUM:
        lead_in = f"This {total_weeks}-week roadmap focuses on closing moderate skill gaps."
    elif severity == SeverityEnum.HIGH:
        lead_in = f"This {total_weeks}-week roadmap targets major missing skills."
    elif severity == SeverityEnum.CRITICAL:
        lead_in = f"This {total_weeks}-week roadmap addresses substantial skill deficiencies."

    skill_names = [r.skill for r in recommendations]
    num_skills = len(skill_names)

    if num_skills == 0:
        skills_str = "no skills"
    elif num_skills == 1:
        skills_str = f"1 skill ({skill_names[0]})"
    else:
        skills_str = f"{num_skills} skills (" + ", ".join(skill_names[:-1]) + f" and {skill_names[-1]})"

    detail = f"This {total_weeks}-week roadmap covers {skills_str} and is expected to improve the student's match score by approximately {expected_improvement:.0f} points."
    return f"{lead_in} {detail}"


def generate_deterministic_roadmap(
    student_id: UUID,
    skill_gap_report: SkillGapReport
) -> CareerRoadmap:
    """Fallback generator when Gemini is bypassed or fails."""
    severity = skill_gap_report.severity
    total_weeks = SEVERITY_WEEKS_MAPPING.get(severity, 1)

    # Sort recommendations: Priority first (HIGH -> MEDIUM -> LOW), then alphabetically by skill name
    priority_order = {PriorityEnum.HIGH: 0, PriorityEnum.MEDIUM: 1, PriorityEnum.LOW: 2}
    sorted_recs = sorted(
        skill_gap_report.recommendations,
        key=lambda r: (priority_order.get(r.priority, 2), r.skill.lower())
    )

    N = len(sorted_recs)
    W = total_weeks

    weeks = [RoadmapWeek(week_number=w + 1, tasks=[]) for w in range(W)]
    if N > 0:
        base_tasks = N // W
        remainder = N % W
        idx = 0
        for w in range(W):
            count = base_tasks + (1 if w < remainder else 0)
            week_recs = sorted_recs[idx : idx + count]
            idx += count
            for rec in week_recs:
                task = build_task_for_skill(rec.skill, w + 1)
                weeks[w].tasks.append(task)

    expected_improvement = sum(r.estimated_improvement_score for r in sorted_recs)
    roadmap_summary = generate_summary(severity, total_weeks, sorted_recs, expected_improvement)

    return CareerRoadmap(
        student_id=student_id,
        total_weeks=total_weeks,
        roadmap_weeks=weeks,
        expected_match_score_improvement=round(expected_improvement, 2),
        overall_confidence=skill_gap_report.overall_confidence,
        roadmap_version="1.0.0",
        generated_from_severity=severity,
        roadmap_summary=roadmap_summary,
    )


def enforce_roadmap_rules(
    roadmap: CareerRoadmap,
    student_id: UUID,
    skill_gap_report: SkillGapReport
) -> CareerRoadmap:
    """Enforces absolute correctness on the parsed LLM roadmap output."""
    roadmap.student_id = student_id
    roadmap.roadmap_version = "1.0.0"

    severity = skill_gap_report.severity
    roadmap.generated_from_severity = severity
    total_weeks = SEVERITY_WEEKS_MAPPING.get(severity, 1)
    roadmap.total_weeks = total_weeks

    # Gather tasks and match to recommendations
    all_tasks = []
    for week in roadmap.roadmap_weeks:
        all_tasks.extend(week.tasks)

    llm_tasks_by_skill = {t.skill.lower().strip(): t for t in all_tasks if t.skill}

    priority_order = {PriorityEnum.HIGH: 0, PriorityEnum.MEDIUM: 1, PriorityEnum.LOW: 2}
    sorted_recs = sorted(
        skill_gap_report.recommendations,
        key=lambda r: (priority_order.get(r.priority, 2), r.skill.lower())
    )

    final_tasks = []
    for rec in sorted_recs:
        skill_key = rec.skill.lower().strip()
        if skill_key in llm_tasks_by_skill:
            llm_task = llm_tasks_by_skill[skill_key]
            # Maintain the description and title from LLM but align structure
            llm_task.skill = rec.skill
            final_tasks.append(llm_task)
        else:
            final_tasks.append(build_task_for_skill(rec.skill, 1))

    # Redistribute tasks evenly across weeks
    N = len(final_tasks)
    W = total_weeks
    weeks = [RoadmapWeek(week_number=w + 1, tasks=[]) for w in range(W)]
    if N > 0:
        base_tasks = N // W
        remainder = N % W
        idx = 0
        for w in range(W):
            count = base_tasks + (1 if w < remainder else 0)
            week_tasks = final_tasks[idx : idx + count]
            idx += count
            for task in week_tasks:
                task.week_number = w + 1
                weeks[w].tasks.append(task)

    roadmap.roadmap_weeks = weeks

    expected_improvement = sum(r.estimated_improvement_score for r in sorted_recs)
    roadmap.expected_match_score_improvement = round(expected_improvement, 2)
    roadmap.roadmap_summary = generate_summary(severity, total_weeks, sorted_recs, expected_improvement)

    return roadmap


# Google ADK Agent Instantiation
career_roadmap_agent = Agent(
    name="career_roadmap_agent",
    instruction=SYSTEM_INSTRUCTION,
    model="gemini-2.5-flash",
    output_schema=CareerRoadmap,
)


def generate_career_roadmap(
    student_profile: StudentProfile,
    skill_gap_report: SkillGapReport,
) -> CareerRoadmap:
    """
    Validates input schemas, generates a structured CareerRoadmap using Gemini
    (if enabled and reachable), and enforces all week mapping, priority sorting,
    and improvement calculations. Falls back immediately on API errors.
    """
    if not isinstance(student_profile, StudentProfile):
        raise ValueError("student_profile must be a valid StudentProfile instance.")
    if not isinstance(skill_gap_report, SkillGapReport):
        raise ValueError("skill_gap_report must be a valid SkillGapReport instance.")

    student_id = student_profile.student_id

    if not USE_LLM_ENRICHMENT:
        return generate_deterministic_roadmap(student_id, skill_gap_report)

    try:
        runner = InMemoryRunner(agent=career_roadmap_agent)
        runner.auto_create_session = True

        current_prompt = (
            f"Student Profile:\n"
            f"student_id: {student_id}\n"
            f"target_role_category: {student_profile.target_role_category}\n\n"
            f"Skill Gap Report:\n"
            f"severity: {skill_gap_report.severity}\n"
            f"recommendations: {[r.model_dump() for r in skill_gap_report.recommendations]}\n"
        )

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        )

        events = runner.run(
            user_id="default_user",
            session_id=f"session_{student_id}",
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
            if isinstance(output, CareerRoadmap):
                parsed_output = output
            elif isinstance(output, dict):
                parsed_output = CareerRoadmap.model_validate(output)
            elif isinstance(output, str):
                parsed_output = CareerRoadmap.model_validate_json(output)

            if parsed_output is not None:
                return enforce_roadmap_rules(parsed_output, student_id, skill_gap_report)

        raise ValueError("Empty or malformed LLM response.")

    except Exception as e:
        print(f"[CAREER ROADMAP AGENT] LLM error: {e}. Falling back to deterministic generator.")
        return generate_deterministic_roadmap(student_id, skill_gap_report)
