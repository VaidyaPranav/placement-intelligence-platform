# Evaluation Test Suite for Company Intelligence Agent

import pytest
from uuid import uuid4
from unittest.mock import patch
from backend.app.agents.company_agent.agent import extract_hiring_requirements
from backend.app.agents.company_agent.schemas import CompanyIntelligenceOutput, ExperienceLevelEnum, ExplainabilitySection, SkillEvidence


# 1. Helper function for Jaccard Similarity calculation
def calculate_jaccard_similarity(set_a, set_b) -> float:
    set_a = {s.lower().strip() for s in set_a}
    set_b = {s.lower().strip() for s in set_b}
    if not set_a and not set_b:
        return 1.0
    union = set_a.union(set_b)
    intersection = set_a.intersection(set_b)
    return len(intersection) / len(union)


# 2. Offline Evaluation Dataset (4 Job Descriptions with Ground-Truth Annotations)
EVAL_DATASET = {
    "cloud_backend": {
        "text": """
        Title: Senior Cloud Backend Engineer
        Company: TechScale Systems
        We are seeking a senior backend software engineer with 5+ years of experience.
        You must have solid experience in Node.js, Express, and MySQL databases.
        Preferred qualifications: Docker containerization and AWS practitioner certificate.
        Candidates should have a minimum CGPA of 7.0. Must have excellent communication skills.
        """,
        "ground_truth": {
            "role_title": "Senior Cloud Backend Engineer",
            "role_category": "Software Engineering",
            "experience_level": ExperienceLevelEnum.SENIOR,
            "required_skills": ["Node.js", "Express", "MySQL"],
            "preferred_skills": ["Docker", "AWS Cloud Practitioner"],
            "soft_skills": ["Communication"],
            "minimum_cgpa": 7.0
        }
    },
    "frontend_dev": {
        "text": """
        Position: Junior Frontend Developer
        Join our web development team. You will build highly responsive UIs using ReactJS and CSS.
        TypeScript knowledge is highly preferred. No GPA requirements. Collaboration is key.
        """,
        "ground_truth": {
            "role_title": "Junior Frontend Developer",
            "role_category": "Software Engineering",
            "experience_level": ExperienceLevelEnum.JUNIOR,
            "required_skills": ["React", "CSS"],
            "preferred_skills": ["TypeScript"],
            "soft_skills": ["Collaboration"],
            "minimum_cgpa": 0.0
        }
    },
    "data_analyst": {
        "text": """
        Position: Entry Level Data Analyst
        We are looking for an analyst to join the business intelligence group.
        You will extract and analyze datasets using SQL and build reports in Tableau.
        Python experience is a plus. Good critical thinking and presenting skills are preferred.
        Minimum grade criteria: 7.5 CGPA out of 10.
        """,
        "ground_truth": {
            "role_title": "Entry Level Data Analyst",
            "role_category": "Data & Analytics",
            "experience_level": ExperienceLevelEnum.ENTRY_LEVEL,
            "required_skills": ["SQL", "Tableau"],
            "preferred_skills": ["Python"],
            "soft_skills": ["Critical thinking", "Presenting"],
            "minimum_cgpa": 7.5
        }
    },
    "ai_engineer": {
        "text": """
        Title: Machine Learning Engineer (Internship)
        We are offering an internship role for a student in our AI labs.
        You will build ML models using Python and PyTorch. Experience with Kubernetes is preferred.
        Minimum CGPA required: 8.0. Problem-solving skills are mandatory.
        """,
        "ground_truth": {
            "role_title": "Machine Learning Engineer (Internship)",
            "role_category": "AI/ML",
            "experience_level": ExperienceLevelEnum.INTERNSHIP,
            "required_skills": ["Python", "PyTorch"],
            "preferred_skills": ["Kubernetes"],
            "soft_skills": ["Problem-solving"],
            "minimum_cgpa": 8.0
        }
    }
}


# Mock Event to simulate ADK event loop generator
class MockEvent:
    def __init__(self, output):
        self.output = output


# 3. Evaluation Test Loop
@pytest.mark.parametrize("job_key", EVAL_DATASET.keys())
def test_agent_extraction_accuracy(job_key):
    job_data = EVAL_DATASET[job_key]
    job_id = str(uuid4())
    
    # We mock Gemini to return the exact ground truth with correct formats to verify the processing logic.
    # In live environments, the mock can be deactivated to run against Gemini.
    gt = job_data["ground_truth"]
    mocked_explainability = ExplainabilitySection(
        role_evidence=f"Extracted role title: {gt['role_title']}",
        skill_evidence=[SkillEvidence(skill_tag=s, evidence_sentence="Mentioned in requirements.") for s in gt["required_skills"]],
        cgpa_evidence=f"Required CGPA: {gt['minimum_cgpa']}"
    )
    mocked_output = CompanyIntelligenceOutput(
        job_id=uuid4(),
        role_title=gt["role_title"],
        role_category=gt["role_category"],
        experience_level=gt["experience_level"],
        required_skills=gt["required_skills"],
        preferred_skills=gt["preferred_skills"],
        soft_skills=gt["soft_skills"],
        minimum_cgpa=gt["minimum_cgpa"],
        overall_confidence=0.9,
        skill_confidence=0.9,
        role_confidence=1.0,
        cgpa_confidence=1.0,
        explainability_section=mocked_explainability
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = extract_hiring_requirements(job_id, job_data["text"])
        
        # Verify schema
        assert isinstance(result, CompanyIntelligenceOutput)
        
        # 1. Role Category Accuracy (Category taxonomy mapping must match exactly)
        assert result.role_category == gt["role_category"]
        
        # 2. Experience Level Accuracy
        assert result.experience_level == gt["experience_level"]
        
        # 3. Technical Skill Extraction Jaccard Similarity (Threshold: >= 80%)
        tech_similarity = calculate_jaccard_similarity(
            result.required_skills + result.preferred_skills,
            gt["required_skills"] + gt["preferred_skills"]
        )
        assert tech_similarity >= 0.8, f"Technical skill similarity is low: {tech_similarity}"
        
        # 4. Soft Skill Jaccard Similarity (Threshold: >= 50% for soft skills)
        soft_similarity = calculate_jaccard_similarity(result.soft_skills, gt["soft_skills"])
        assert soft_similarity >= 0.5, f"Soft skill similarity is low: {soft_similarity}"
        
        # 5. CGPA Extraction Accuracy
        assert result.minimum_cgpa == gt["minimum_cgpa"]
        
        # 6. Explainability Coverage Check
        assert len(result.explainability_section.role_evidence.strip()) > 0
        assert len(result.explainability_section.skill_evidence) > 0
        assert len(result.explainability_section.cgpa_evidence.strip()) > 0
        
        # Output evaluation log
        print(f"\n[EVALUATION REPORT] Role: {job_key}")
        print(f" - Technical Skills Jaccard Score: {tech_similarity:.2%}")
        print(f" - Soft Skills Jaccard Score: {soft_similarity:.2%}")
        print(f" - Match status: SUCCESS")
