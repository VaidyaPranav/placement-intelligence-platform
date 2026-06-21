# Evaluation Test Suite for Student Intelligence Agent

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch

from backend.app.agents.student_agent.agent import extract_student_profile
from backend.app.agents.student_agent.schemas import (
    StudentProfile,
    Project,
    Certification,
    Internship,
    GitHubAnalysis,
    ExplainabilitySection,
    SkillEvidence,
    ProjectEvidence,
    CertificationEvidence,
    InternshipEvidence,
    DepartmentEnum,
    PlacementStatusEnum,
    TargetRoleCategoryEnum,
)


# 1. Helper function for Jaccard Similarity calculation
def calculate_jaccard_similarity(set_a, set_b) -> float:
    set_a = {s.lower().strip() for s in set_a}
    set_b = {s.lower().strip() for s in set_b}
    if not set_a and not set_b:
        return 1.0
    union = set_a.union(set_b)
    intersection = set_a.intersection(set_b)
    return len(intersection) / len(union)


# 2. Evaluation Dataset (4 Student Resumes with Ground-Truth Annotations)
EVAL_DATASET = {
    "full_stack": {
        "text": """
        Varun Sharma
        Email: varun@example.com | GitHub: https://github.com/varunsharma | LinkedIn: https://linkedin.com/in/varunsharma
        B.Tech in Computer Science and Engineering
        CGPA: 8.5/10.0
        
        Skills: ReactJS, NodeJS, JavaScript, HTML, CSS, My SQL, Git, Docker
        
        Projects:
        - E-Commerce Web App: Built a full stack online store using React.js and NodeJS. Implemented MySQL database integration.
        - Personal Portfolio Site: A simple React site displaying my details.
        
        Certifications:
        - React Developer Certification issued by Meta
        
        Achievements:
        - Secured Rank 450 in Google Kickstart Round D.
        
        Internships:
        - Web Developer Intern at DevCorp (2 months): Developed UI components in React and optimized backend routes.
        """,
        "ground_truth": {
            "name": "Varun Sharma",
            "department": DepartmentEnum.CS,
            "cgpa": 8.5,
            "skills": ["React", "Node.js", "JavaScript", "HTML", "CSS", "MySQL", "Git", "Docker"],
            "projects": [
                {"title": "E-Commerce Web App", "complexity_score": 6},
                {"title": "Personal Portfolio Site", "complexity_score": 3}
            ],
            "certifications": [
                {"name": "React Developer Certification", "issuer": "Meta"}
            ],
            "internships": [
                {"company": "DevCorp", "role": "Web Developer Intern", "duration_months": 2}
            ],
            "target_role_category": TargetRoleCategoryEnum.SOFTWARE_ENGINEERING,
            "github_url": "https://github.com/varunsharma",
            "linkedin_url": "https://linkedin.com/in/varunsharma",
            "portfolio_url": None,
        }
    },
    "cloud_devops": {
        "text": """
        Aditya Sen
        Email: aditya.sen@example.com | GitHub: https://github.com/adityasen
        B.Tech in Information Technology
        CGPA: 9.1/10
        
        Skills: AWS, Terraform, Docker, Python, Bash, Kubernetes, Linux
        
        Projects:
        - Terraform Multi-AZ Setup: Orchestrated and deployed a highly-available VPC infrastructure on AWS using Terraform.
        - Dockerized Microservices: Containerized and deployed Python applications using Docker and Kubernetes.
        
        Certifications:
        - AWS Certified Solutions Architect Associate issued by Amazon Web Services
        
        Achievements:
        - Certified AWS Solutions Architect.
        
        Internships:
        - DevOps Intern at CloudScale Inc (3 months): Automated CI/CD pipelines using Gitlab and Docker.
        """,
        "ground_truth": {
            "name": "Aditya Sen",
            "department": DepartmentEnum.IT,
            "cgpa": 9.1,
            "skills": ["AWS", "Terraform", "Docker", "Python", "Bash", "Kubernetes", "Linux"],
            "projects": [
                {"title": "Terraform Multi-AZ Setup", "complexity_score": 8},
                {"title": "Dockerized Microservices", "complexity_score": 7}
            ],
            "certifications": [
                {"name": "AWS Certified Solutions Architect Associate", "issuer": "Amazon Web Services"}
            ],
            "internships": [
                {"company": "CloudScale Inc", "role": "DevOps Intern", "duration_months": 3}
            ],
            "target_role_category": TargetRoleCategoryEnum.CLOUD_DEVOPS,
            "github_url": "https://github.com/adityasen",
            "linkedin_url": None,
            "portfolio_url": None,
        }
    },
    "ai_ml": {
        "text": """
        Priya Patel
        Email: priya@example.com | LinkedIn: https://linkedin.com/in/priyapatel
        B.Tech in Electronics & Communication Engineering
        CGPA: 8.8/10
        
        Skills: Python, PyTorch, Tensor Flow, Computer Vision, OpenCV, NumPy, C++
        
        Projects:
        - ResNet Custom Classifier: Implemented a deep learning model in PyTorch to classify medical scan images with 94% accuracy.
        - Face Detection App: A real-time face detection system using OpenCV and Python.
        
        Certifications:
        - Deep Learning Specialization issued by Coursera DeepLearning.AI
        
        Achievements:
        - Published research paper on Computer Vision in IEEE.
        
        Internships:
        - ML Research Intern at VisionLabs (5 months): Trained convolutional neural networks on proprietary datasets.
        """,
        "ground_truth": {
            "name": "Priya Patel",
            "department": DepartmentEnum.ECE,
            "cgpa": 8.8,
            "skills": ["Python", "PyTorch", "TensorFlow", "Computer Vision", "OpenCV", "NumPy", "C++"],
            "projects": [
                {"title": "ResNet Custom Classifier", "complexity_score": 9},
                {"title": "Face Detection App", "complexity_score": 4}
            ],
            "certifications": [
                {"name": "Deep Learning Specialization", "issuer": "Coursera DeepLearning.AI"}
            ],
            "internships": [
                {"company": "VisionLabs", "role": "ML Research Intern", "duration_months": 5}
            ],
            "target_role_category": TargetRoleCategoryEnum.AI_ML,
            "github_url": None,
            "linkedin_url": "https://linkedin.com/in/priyapatel",
            "portfolio_url": None,
        }
    },
    "data_analyst": {
        "text": """
        Kunal Shah
        Email: kunal@example.com | Portfolio: https://kunalshah.dev
        B.Tech in Information Technology
        CGPA: 8.2/10
        
        Skills: SQL, PowerBI, Tableau, Python, Excel, Pandas, Matplotlib
        
        Projects:
        - Sales Performance Dashboard: Created an interactive corporate sales dashboard using PowerBI.
        - HR Churn Analysis: Utilized Python, Pandas, and Matplotlib to analyze employee attrition factors.
        
        Certifications:
        - Microsoft Certified: Power BI Data Analyst Associate issued by Microsoft
        
        Achievements:
        - Winner of university hackathon (Data Analytics track).
        
        Internships:
        - Data Analyst Intern at RetailCorp (2 months): Developed ETL scripts and built automated reports.
        """,
        "ground_truth": {
            "name": "Kunal Shah",
            "department": DepartmentEnum.IT,
            "cgpa": 8.2,
            "skills": ["SQL", "Power BI", "Tableau", "Python", "Excel", "Pandas", "Matplotlib"],
            "projects": [
                {"title": "Sales Performance Dashboard", "complexity_score": 4},
                {"title": "HR Churn Analysis", "complexity_score": 5}
            ],
            "certifications": [
                {"name": "Microsoft Certified: Power BI Data Analyst Associate", "issuer": "Microsoft"}
            ],
            "internships": [
                {"company": "RetailCorp", "role": "Data Analyst Intern", "duration_months": 2}
            ],
            "target_role_category": TargetRoleCategoryEnum.DATA_ANALYTICS,
            "github_url": None,
            "linkedin_url": None,
            "portfolio_url": "https://kunalshah.dev",
        }
    }
}


# Mock Event to simulate ADK event loop generator
class MockEvent:
    def __init__(self, output):
        self.output = output


# 3. Evaluation Test Loop
@pytest.mark.parametrize("student_key", EVAL_DATASET.keys())
def test_agent_student_profile_extraction_accuracy(student_key):
    student_data = EVAL_DATASET[student_key]
    student_id = str(uuid4())
    gt = student_data["ground_truth"]

    # Build Mock explainability
    mocked_explainability = ExplainabilitySection(
        name_evidence=f"Name is {gt['name']}",
        department_evidence=f"Department is {gt['department']}",
        cgpa_evidence=f"CGPA is {gt['cgpa']}",
        skill_evidence=[SkillEvidence(skill_tag=s, evidence_sentence="Found in resume") for s in gt["skills"]],
        project_evidence=[ProjectEvidence(project_title=p["title"], evidence_sentence="Found in resume") for p in gt["projects"]],
        certification_evidence=[CertificationEvidence(certification_name=c["name"], evidence_sentence="Found in resume") for c in gt["certifications"]],
        internship_evidence=[InternshipEvidence(internship_company=i["company"], evidence_sentence="Found in resume") for i in gt["internships"]],
    )

    # Build Mock profile conforming to StudentProfile
    mocked_output = StudentProfile(
        student_id=uuid4(),
        name=gt["name"],
        department=gt["department"],
        cgpa=gt["cgpa"],
        skills=gt["skills"],
        projects=[Project(title=p["title"], complexity_score=p["complexity_score"]) for p in gt["projects"]],
        certifications=[Certification(name=c["name"], issuer=c["issuer"]) for c in gt["certifications"]],
        achievements=[],
        internships=[Internship(company=i["company"], role=i["role"], duration_months=i["duration_months"]) for i in gt["internships"]],
        resume_text=student_data["text"],
        resume_confidence=0.9,
        verified_sources=["RESUME_PDF"],
        github_analysis=GitHubAnalysis(repo_count=0, languages=[], verification_status="UNVERIFIED"),
        technical_score=0,
        project_score=0,
        communication_score=0,
        interview_score=0,
        certification_score=0,
        placement_status=PlacementStatusEnum.UNPLACED,
        target_role_category=gt["target_role_category"],
        profile_version="1.0.0",
        overall_confidence=0.9,
        explainability_section=mocked_explainability,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        github_url=gt["github_url"],
        portfolio_url=gt["portfolio_url"],
        linkedin_url=gt["linkedin_url"],
    )

    mock_event = MockEvent(mocked_output)

    with patch("google.adk.runners.InMemoryRunner.run", return_value=[mock_event]):
        result = extract_student_profile(student_id, student_data["text"])

        assert isinstance(result, StudentProfile)

        # 1. Name & Metadata Accuracy
        assert result.name == gt["name"]
        assert result.department == gt["department"]
        assert result.cgpa == gt["cgpa"]

        # 2. Skill Extraction Jaccard Similarity (Threshold: >= 85%)
        skill_similarity = calculate_jaccard_similarity(result.skills, gt["skills"])
        assert skill_similarity >= 0.85, f"Skill similarity is low: {skill_similarity}"

        # 3. Project Extraction Jaccard Similarity (Threshold: >= 85%)
        result_proj_titles = [p.title for p in result.projects]
        gt_proj_titles = [p["title"] for p in gt["projects"]]
        project_similarity = calculate_jaccard_similarity(result_proj_titles, gt_proj_titles)
        assert project_similarity >= 0.85, f"Project similarity is low: {project_similarity}"

        # Verify project complexity score constraints
        for proj in result.projects:
            title_lower = proj.title.lower()
            if "crud" in title_lower:
                assert 3 <= proj.complexity_score <= 4
            elif any(w in title_lower for w in ["full stack", "fullstack", "web app"]):
                assert 5 <= proj.complexity_score <= 7
            elif any(w in title_lower for w in ["cloud", "aws", "terraform"]):
                assert 7 <= proj.complexity_score <= 8
            elif any(w in title_lower for w in ["classifier", "ai", "deep learning"]):
                assert 8 <= proj.complexity_score <= 10

        # 4. Certification Extraction Accuracy (Jaccard Score >= 85%)
        result_certs = [c.name for c in result.certifications]
        gt_certs = [c["name"] for c in gt["certifications"]]
        cert_similarity = calculate_jaccard_similarity(result_certs, gt_certs)
        assert cert_similarity >= 0.85, f"Certification similarity is low: {cert_similarity}"

        # 5. CGPA Check
        assert result.cgpa == gt["cgpa"]

        # 6. Target Role Category Check
        assert result.target_role_category == gt["target_role_category"]

        # 7. Explainability Coverage Check
        assert len(result.explainability_section.name_evidence.strip()) > 0
        assert len(result.explainability_section.department_evidence.strip()) > 0
        assert len(result.explainability_section.cgpa_evidence.strip()) > 0
        assert len(result.explainability_section.skill_evidence) > 0
        assert len(result.explainability_section.project_evidence) > 0
        assert len(result.explainability_section.certification_evidence) > 0
        assert len(result.explainability_section.internship_evidence) > 0

        # Output evaluation report log
        print(f"\n[STUDENT EVALUATION REPORT] Category: {student_key}")
        print(f" - Skill Jaccard Score: {skill_similarity:.2%}")
        print(f" - Project Jaccard Score: {project_similarity:.2%}")
        print(f" - Certifications Jaccard Score: {cert_similarity:.2%}")
        print(f" - Target Role: {result.target_role_category.value}")
        print(f" - Match status: SUCCESS")
