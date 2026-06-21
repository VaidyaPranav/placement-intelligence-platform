# Placement Intelligence Platform (PIP)

Placement Intelligence Platform (PIP) is a production-ready, multi-agent AI system designed to streamline recruitment and career preparation. It automatically extracts structured intelligence from resumes and job descriptions using Google Gemini, evaluates candidate fit, details skill gaps, generates study roadmaps, and compiles tailored interview preparation packages.

## Key Features

- **Six Cooperative AI Agents:** Coordinated execution across specialized agents (Student, Company, Ranking, Skill Gap, Career Roadmap, and Interview agents).
- **Graceful Failure Orchestration:** The pipeline is fault-tolerant; if downstream agents fail, it reports a `PARTIAL_SUCCESS` and returns all completed modules.
- **Modern Dashboard UI:** A beautiful dark-mode glassmorphic dashboard built using React, Vite, TypeScript, and Recharts, with automated PDF parsing and charts.
- **Containerized Architecture:** Fully containerized with Docker & Docker Compose for immediate production-ready local or cloud deployment.

---

## System Architecture

The platform follows a layered API & Orchestration architecture:

```
[Resume PDF / Text] ──> [Student Agent] ──┐
                                          ├──> [Ranking Agent] ──> [Skill Gap Agent] ──> [Roadmap Agent] ──> [Interview Agent]
[Job Description]   ──> [Company Agent] ──┘
```

For more details on the agent flows and network topology, see the [Architecture Documentation](docs/architecture.md).

---

## API Endpoints

The FastAPI backend exposes the following endpoints (prefixed with `/api/v1`):

- `GET /health` - Health check status
- `POST /api/v1/student/analyze` - Extract student profile
- `POST /api/v1/job/analyze` - Extract hiring requirements
- `POST /api/v1/match` - Candidate-job matching
- `POST /api/v1/skill-gap` - Gap assessment
- `POST /api/v1/roadmap` - Study roadmap generation
- `POST /api/v1/interview` - Tailored prep pack compilation
- `POST /api/v1/full-analysis` - Orchestrate the full sequence

For payload formats and interactive examples, see the [API Documentation](docs/api.md).

---

## Setup Instructions

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/) (Version 20.10+)
- [Node.js](https://nodejs.org/) (Version 20+ for local development)
- [Python](https://www.python.org/) (Version 3.11 for local development)
- A **Google Gemini API Key** (Set via `GOOGLE_API_KEY` env var)

### Environment Configuration
Copy the template environment file to create your local configurations:
```bash
cp .env.example .env
```
Edit the newly created `.env` file and specify your `GOOGLE_API_KEY`:
```env
GOOGLE_API_KEY=<your-key>
USE_LLM_ENRICHMENT=True
ENABLE_AUTOMATIC_FALLBACK=True
```

---

## Startup Instructions

### 1. Docker Startup (Recommended)
You can start the entire application (both backend and frontend) with a single command:
```bash
docker compose up --build
```
- Access the **Frontend Application** at: `http://localhost`
- Access the **FastAPI Swagger Docs** at: `http://localhost:8000/docs`

### 2. Backend Local Startup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Local Startup
```bash
cd frontend
npm install
npm run dev
```
By default, the Vite dev server runs at `http://localhost:5173`.

---

## Testing & Quality Assurance

To validate the test suite locally:

### Running Backend Unit/Integration Tests
```bash
cd backend
python -m pytest
```

### Building Frontend Assets
```bash
cd frontend
npm run build
```

---

## Screenshots

*(Insert visual walk-throughs and dashboards here)*

---

## Future Improvements

1. **Persistent Datastores:** Add database configurations (e.g. PostgreSQL or MongoDB) for archiving analysis histories.
2. **Batch Processing:** Add support for running matches across a bulk list of resumes against a job description.
3. **Advanced PDF Extraction:** Incorporate OCR libraries for handling scanned image-based resume uploads.
4. **Agent Self-Correction:** Incorporate reflection steps where agents self-correct outputs using validation loops.
