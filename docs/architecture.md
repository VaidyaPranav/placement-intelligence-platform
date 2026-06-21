# Placement Intelligence Platform Architecture

This document describes the architectural layout, components, and data flow pipelines of the Placement Intelligence Platform (PIP).

## Overview

PIP is a multi-agent system designed to analyze resumes and job descriptions to provide structured match scores, skill gap reports, career roadmaps, and interview preparation packages.

```mermaid
graph TD
    Resume["Resume Text / PDF"] --> SA["Student Agent"]
    JD["Job Description Text"] --> CA["Company Agent"]
    SA --> SP["Student Profile"]
    CA --> HR["Hiring Requirements"]
    
    SP & HR --> RA["Ranking Agent"]
    RA --> MR["Match Result"]
    
    SP & HR & MR --> SGA["Skill Gap Agent"]
    SGA --> SGR["Skill Gap Report"]
    
    SP & HR & MR & SGR --> CRA["Career Roadmap Agent"]
    CRA --> CR["Career Roadmap"]
    
    SP & HR & MR & SGR --> IA["Interview Agent"]
    IA --> IP["Interview Prep Pack"]
    
    SP & HR & MR & SGR & CR & IP --> PAR["Placement Analysis Result"]
```

## System Integration Stack

The flow of requests from the user interface down to the specialized LLM intelligence agents is structured as follows:

```mermaid
graph TD
    User([User / Recruiter]) --> Frontend["React / Vite Frontend"]
    Frontend -->|HTTP Requests| FastAPI["FastAPI REST API Layer"]
    FastAPI -->|Orchestration Request| Orchestrator["Placement Pipeline Orchestrator"]
    Orchestrator -->|Executes parallel/sequential agents| Agents["Multi-Agent Swarm"]
    
    subgraph Agents
        direction TB
        A1["Student Agent"]
        A2["Company Agent"]
        A3["Ranking Agent"]
        A4["Skill Gap Agent"]
        A5["Career Roadmap Agent"]
        A6["Interview Agent"]
    end
```

## Agent Coordination Details

1. **Student Agent**: Extracts normalized tech skills, experience levels, certifications, and educational credentials from student resumes.
2. **Company Agent**: Extracts target roles, core tech stack keywords, minimum experience, and required/preferred credentials from job descriptions.
3. **Ranking Agent**: Computes semantic match scores and maps student profiles against job descriptions.
4. **Skill Gap Agent**: Performs a detailed comparison of student skills versus job requirements, categorizing gaps and identifying missing skills.
5. **Career Roadmap Agent**: Produces actionable learning milestones, target timelines, and resource recommendations to close identified gaps.
6. **Interview Agent**: Generates tailored behavioral and technical questions, reference answers, evaluation rubrics, and overall preparation guidance.
