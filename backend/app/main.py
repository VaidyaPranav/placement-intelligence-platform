from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router as api_router
from backend.app.config import PIPELINE_VERSION

app = FastAPI(
    title="Placement Intelligence Platform API",
    description="Orchestrator and API Layer for Multi-Agent Student/Job Placement Intelligence",
    version=PIPELINE_VERSION,
)

# CORS Configuration
# Open CORS for hackathon/demo deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", summary="Root endpoint returning metadata")
def read_root():
    return {
        "service": "Placement Intelligence Platform",
        "version": PIPELINE_VERSION,
        "status": "running",
    }


@app.get("/health", summary="Health check endpoint")
def health_check():
    return {
        "status": "healthy",
        "pipeline_version": PIPELINE_VERSION,
    }