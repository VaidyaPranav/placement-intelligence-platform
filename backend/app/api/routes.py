# FastAPI Route Definitions

import os
from google.genai import Client
import backend.app.config as config
from backend.app.config import GOOGLE_API_KEY
from fastapi import APIRouter, HTTPException
from backend.app.agents.student_agent import extract_student_profile, StudentProfile
from backend.app.agents.company_agent import extract_hiring_requirements, CompanyIntelligenceOutput
from backend.app.agents.ranking_agent import rank_student_against_job, MatchResult
from backend.app.agents.skill_gap_agent import generate_skill_gap_report, SkillGapReport
from backend.app.agents.career_roadmap_agent import generate_career_roadmap, CareerRoadmap
from backend.app.agents.interview_agent import generate_interview_preparation_report, InterviewPreparationReport
from backend.app.orchestrators.placement_pipeline import run_full_placement_analysis
from backend.app.orchestrators.schemas import PlacementAnalysisResult

from .schemas import (
    StudentAnalyzeRequest,
    JobAnalyzeRequest,
    MatchRequest,
    SkillGapRequest,
    RoadmapRequest,
    InterviewRequest,
    FullAnalysisRequest,
    AIStatusResponse,
)

router = APIRouter()


@router.post("/student/analyze", response_model=StudentProfile, summary="Extract student profile from resume")
def analyze_student(req: StudentAnalyzeRequest):
    try:
        return extract_student_profile(req.student_id, req.resume_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job/analyze", response_model=CompanyIntelligenceOutput, summary="Extract job requirements from JD")
def analyze_job(req: JobAnalyzeRequest):
    try:
        return extract_hiring_requirements(req.job_id, req.job_description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match", response_model=MatchResult, summary="Match student against requirements")
def match_student(req: MatchRequest):
    try:
        return rank_student_against_job(req.student_profile, req.hiring_requirements)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skill-gap", response_model=SkillGapReport, summary="Compute skill gap analysis")
def skill_gap(req: SkillGapRequest):
    try:
        return generate_skill_gap_report(req.student_profile, req.hiring_requirements, req.match_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/roadmap", response_model=CareerRoadmap, summary="Generate multi-week roadmap")
def roadmap(req: RoadmapRequest):
    try:
        return generate_career_roadmap(req.student_profile, req.skill_gap_report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview", response_model=InterviewPreparationReport, summary="Generate role-specific prep pack")
def interview(req: InterviewRequest):
    try:
        return generate_interview_preparation_report(
            req.student_profile, req.hiring_requirements, req.match_result, req.skill_gap_report
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-analysis", response_model=PlacementAnalysisResult, summary="Execute full multi-agent orchestration pipeline")
def full_analysis(req: FullAnalysisRequest):
    try:
        return run_full_placement_analysis(
            req.student_id, req.resume_text, req.job_id, req.job_description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-status", response_model=AIStatusResponse, summary="Get real-time Gemini API status")
def get_ai_status():
    api_key = GOOGLE_API_KEY.strip()
    api_configured = bool(api_key)
    
    llm_enabled = getattr(config, "USE_LLM_ENRICHMENT", True)
    fallback_enabled = getattr(config, "ENABLE_AUTOMATIC_FALLBACK", True)
    
    if not api_configured:
        return {
            "llm_enrichment_enabled": llm_enabled,
            "fallback_enabled": fallback_enabled,
            "gemini_api_configured": False,
            "status": "API_KEY_MISSING"
        }
        
    try:
        # Check connectivity using a very fast, minimal token generation call.
        client = Client(api_key=GOOGLE_API_KEY)
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents="hi",
            config={"max_output_tokens": 1}
        )
        status = "AI_ACTIVE"
    except Exception as e:
        print(f"[AI STATUS CHECK] Gemini connectivity failed: {e}")
        status = "FALLBACK_MODE" if fallback_enabled else "API_KEY_MISSING"
        
    return {
        "llm_enrichment_enabled": llm_enabled,
        "fallback_enabled": fallback_enabled,
        "gemini_api_configured": api_configured,
        "status": status
    }
