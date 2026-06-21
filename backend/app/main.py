from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router as api_router
from backend.app.config import PIPELINE_VERSION

app = FastAPI(
    title="Placement Intelligence Platform API",
    description="Orchestrator and API Layer for Multi-Agent Student/Job Placement Intelligence",
    version=PIPELINE_VERSION
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://placement-intelligence-platform-24k6cldo3.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with Prefix
app.include_router(api_router, prefix="/api/v1")


@app.get("/", summary="Root endpoint returning metadata")
def read_root():
    return {
        "service": "Placement Intelligence Platform",
        "version": PIPELINE_VERSION,
        "status": "running"
    }


@app.get("/health", summary="Health check endpoint")
def health_check():
    return {
        "status": "healthy",
        "pipeline_version": PIPELINE_VERSION
    }