# Placement Pipeline Orchestrator

import time
from typing import List
from backend.app.orchestrators.schemas import PlacementAnalysisResult, PipelineStatusEnum
from backend.app.agents.student_agent import extract_student_profile
from backend.app.agents.company_agent import extract_hiring_requirements
from backend.app.agents.ranking_agent import rank_student_against_job
from backend.app.agents.skill_gap_agent import generate_skill_gap_report
from backend.app.agents.career_roadmap_agent import generate_career_roadmap
from backend.app.agents.interview_agent import generate_interview_preparation_report
from backend.app.config import PIPELINE_VERSION


def run_full_placement_analysis(
    student_id: str,
    resume_text: str,
    job_id: str,
    job_description: str
) -> PlacementAnalysisResult:
    """
    Executes the six placement intelligence agents in dependency order.
    Catches failures per step, records error logs, tracks step statuses,
    and returns a structured PlacementAnalysisResult.
    """
    start_time = time.time()
    errors: List[str] = []
    execution_steps_completed: List[str] = []
    execution_steps_failed: List[str] = []

    student_profile = None
    hiring_requirements = None
    match_result = None
    skill_gap_report = None
    career_roadmap = None
    interview_report = None

    # STEP 1: Student Agent
    try:
        student_profile = extract_student_profile(student_id, resume_text)
        execution_steps_completed.append("Student Agent")
    except Exception as e:
        execution_steps_failed.append("Student Agent")
        errors.append(f"Student Agent failed: {str(e)}")

    # STEP 2: Company Agent
    try:
        hiring_requirements = extract_hiring_requirements(job_id, job_description)
        execution_steps_completed.append("Company Agent")
    except Exception as e:
        execution_steps_failed.append("Company Agent")
        errors.append(f"Company Agent failed: {str(e)}")

    # STEP 3: Ranking Agent
    if student_profile and hiring_requirements:
        try:
            match_result = rank_student_against_job(student_profile, hiring_requirements)
            execution_steps_completed.append("Ranking Agent")
        except Exception as e:
            execution_steps_failed.append("Ranking Agent")
            errors.append(f"Ranking Agent failed: {str(e)}")
    else:
        execution_steps_failed.append("Ranking Agent")
        errors.append("Ranking Agent skipped: missing required student profile or hiring requirements.")

    # STEP 4: Skill Gap Agent
    if student_profile and hiring_requirements and match_result:
        try:
            skill_gap_report = generate_skill_gap_report(student_profile, hiring_requirements, match_result)
            execution_steps_completed.append("Skill Gap Agent")
        except Exception as e:
            execution_steps_failed.append("Skill Gap Agent")
            errors.append(f"Skill Gap Agent failed: {str(e)}")
    else:
        execution_steps_failed.append("Skill Gap Agent")
        errors.append("Skill Gap Agent skipped: missing required inputs (profile, requirements, or match).")

    # STEP 5: Career Roadmap Agent
    if student_profile and skill_gap_report:
        try:
            career_roadmap = generate_career_roadmap(student_profile, skill_gap_report)
            execution_steps_completed.append("Career Roadmap Agent")
        except Exception as e:
            execution_steps_failed.append("Career Roadmap Agent")
            errors.append(f"Career Roadmap Agent failed: {str(e)}")
    else:
        execution_steps_failed.append("Career Roadmap Agent")
        errors.append("Career Roadmap Agent skipped: missing required student profile or skill gap report.")

    # STEP 6: Interview Agent
    if student_profile and hiring_requirements and match_result and skill_gap_report:
        try:
            interview_report = generate_interview_preparation_report(
                student_profile, hiring_requirements, match_result, skill_gap_report
            )
            execution_steps_completed.append("Interview Agent")
        except Exception as e:
            execution_steps_failed.append("Interview Agent")
            errors.append(f"Interview Agent failed: {str(e)}")
    else:
        execution_steps_failed.append("Interview Agent")
        errors.append("Interview Agent skipped: missing required inputs (profile, requirements, match, or skill gap).")

    total_time = round(time.time() - start_time, 4)

    # Status logic
    total_steps = 6
    succeeded_steps_count = len(execution_steps_completed)

    if succeeded_steps_count == total_steps:
        status = PipelineStatusEnum.SUCCESS
    elif succeeded_steps_count > 0:
        status = PipelineStatusEnum.PARTIAL_SUCCESS
    else:
        status = PipelineStatusEnum.FAILED

    return PlacementAnalysisResult(
        student_profile=student_profile,
        hiring_requirements=hiring_requirements,
        match_result=match_result,
        skill_gap_report=skill_gap_report,
        career_roadmap=career_roadmap,
        interview_report=interview_report,
        pipeline_status=status,
        errors=errors,
        execution_steps_completed=execution_steps_completed,
        execution_steps_failed=execution_steps_failed,
        total_execution_time_seconds=total_time,
        pipeline_version=PIPELINE_VERSION
    )
