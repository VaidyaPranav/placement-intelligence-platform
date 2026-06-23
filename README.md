# Placement Intelligence Platform (PIP)

## AI-Powered Multi-Agent Career Readiness & Recruitment Intelligence System

Placement Intelligence Platform (PIP) is a full-stack AI-powered multi-agent system that helps students evaluate their placement readiness and assists recruiters in assessing candidate suitability more effectively.

The platform analyzes a student's resume against a target job description and generates:

* Student Profile Analysis
* Job Requirement Extraction
* Match Score Evaluation
* Skill Gap Analysis
* Personalized Career Roadmap
* Interview Preparation Pack

---

# Problem Statement

Students often apply for jobs without understanding how well their skills align with company requirements.

Traditional resume screening systems usually provide only a simple score and fail to explain:

* Why a candidate is a good or poor fit
* Which skills are missing
* How missing skills affect employability
* What actions can improve placement readiness

Recruiters and placement teams also spend significant effort manually reviewing resumes.

PIP addresses these challenges through a coordinated multi-agent architecture that transforms resumes and job descriptions into actionable placement intelligence.

---

# Key Features

## Resume Intelligence

Extracts:

* Skills
* Projects
* Certifications
* Education Details
* Academic Performance

from uploaded resumes.

## Job Intelligence

Extracts:

* Required Skills
* Preferred Skills
* Eligibility Requirements
* Hiring Criteria

from job descriptions.

## Candidate Ranking

Generates:

* Match Score
* Recommendation Category
* Eligibility Status

## Skill Gap Analysis

Identifies:

* Missing Skills
* Priority Improvements
* Estimated Score Improvements

## Career Roadmap Generation

Creates:

* Weekly Learning Plans
* Personalized Improvement Paths
* Milestone-Based Roadmaps

## Interview Preparation

Generates:

* Technical Questions
* Behavioral Questions
* Readiness Assessments

---

# Multi-Agent Architecture

The platform is powered by six specialized agents:

### 1. Student Intelligence Agent

Converts unstructured resumes into structured student profiles.

### 2. Company Intelligence Agent

Converts job descriptions into structured hiring requirements.

### 3. Ranking Agent

Compares candidate profiles against job requirements.

### 4. Skill Gap Agent

Identifies missing skills and improvement opportunities.

### 5. Career Roadmap Agent

Generates personalized learning roadmaps.

### 6. Interview Agent

Produces interview preparation content.

---

# Pipeline Flow

Student Resume
↓
Student Agent
↓
Job Description
↓
Company Agent
↓
Ranking Agent
↓
Skill Gap Agent
↓
Career Roadmap Agent
↓
Interview Agent
↓
Placement Intelligence Report

---

# Hybrid AI + Fallback Architecture

PIP implements a Hybrid AI + Deterministic Fallback Architecture.

## AI Mode

When Gemini API services are available:

* Student Agent uses LLM-powered extraction
* Company Agent uses LLM-powered extraction
* Enhanced understanding of resumes and job descriptions

## Fallback Mode

If:

* API quotas are exhausted
* Network failures occur
* API keys become invalid
* Gemini services become unavailable

The platform automatically switches to deterministic extraction logic.

This guarantees uninterrupted operation and improves reliability.

---

# Course Concepts Demonstrated

This project demonstrates multiple concepts covered throughout the course:

## Multi-Agent Systems

Six specialized agents collaborate to solve a complex placement intelligence problem.

## Agent Orchestration

A centralized orchestration layer manages execution flow, dependencies, validation, and fault tolerance.

## Antigravity-Assisted Development

Antigravity was used throughout:

* Planning
* Architecture Design
* Implementation
* Testing
* Debugging
* Refinement

## Security Features

Implemented:

* Environment-based API key management
* Validation layers
* Error handling
* Automated fallback mechanisms

## Agent Skills

Implemented skills include:

* Resume Intelligence
* Job Intelligence
* Candidate Ranking
* Skill Gap Analysis
* Career Planning
* Interview Preparation

## Deployability

Implemented through:

* Docker
* Docker Compose
* Render
* Vercel
* CI/CD Pipelines

---

# Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* Gemini API
* PyPDF

## Frontend

* React
* TypeScript
* Vite
* Axios
* Recharts

## DevOps

* Docker
* Docker Compose
* GitHub Actions
* Render
* Vercel

---

# Project Structure

```text
Placement-Intelligence/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── orchestrators/
│   │   ├── api/
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   ├── services/
│   │   └── types/
│
├── docker-compose.yml
├── README.md
└── .env.example
```

# Local Setup

## Clone Repository

```bash
git clone https://github.com/VaidyaPranav/placement-intelligence-platform.git

cd placement-intelligence-platform
```

## Backend Setup

```bash
pip install -r requirements.txt

python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

USE_LLM_ENRICHMENT=True

ENABLE_AUTOMATIC_FALLBACK=True
```

---

# Deployment

## Backend Deployment

Platform:

* Render

## Frontend Deployment

Platform:

* Vercel

## Containerization

Supported through:

```bash
docker-compose up --build
```

---

# Testing

Run all tests:

```bash
python -m pytest
```

The project includes:

* Agent Tests
* API Tests
* Orchestrator Tests
* End-to-End Integration Tests

More than 150 automated tests pass successfully.

---

# Future Enhancements

Planned improvements include:

* Recruiter Portal
* Placement Cell Dashboard
* Job Posting Management
* Learning Resource Recommendations
* Interview Simulation Agents
* Analytics Dashboard
* Multi-Company Candidate Ranking

---

# Live Demo

Frontend:
https://placement-intelligence-platform-eight.vercel.app

Backend:
https://placement-intelligence-platform-7v0p.onrender.com

---

# Author

Pranav Vaidya

Placement Intelligence Platform (PIP)

AI-Powered Multi-Agent Career Readiness & Recruitment Intelligence System
