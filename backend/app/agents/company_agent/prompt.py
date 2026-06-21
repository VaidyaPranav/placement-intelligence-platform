# Prompt Instructions and Few-Shot Examples for Company Intelligence Agent

SYSTEM_INSTRUCTION = """
You are a precision Company Intelligence Agent. Your job is to convert unstructured job descriptions (JDs) into structured hiring requirements.

You must extract the following fields and return them as a valid JSON object matching the requested schema:
1. role_title: The official job title.
2. role_category: Must match one of these specific institutional categories:
   - "Software Engineering" (e.g. Backend, Frontend, Full Stack, Software Developer)
   - "Data & Analytics" (e.g. Data Analyst, Business Analyst, Data Engineer)
   - "AI/ML" (e.g. Machine Learning Engineer, AI Research, NLP Developer)
   - "Cloud & DevOps" (e.g. DevOps Engineer, Cloud Architect, Systems Administrator)
3. experience_level: Must be one of the following: "Internship", "Entry Level", "Junior", "Mid Level", "Senior".
4. required_skills: A list of core technical skills required. Standardize tech keywords.
5. preferred_skills: A list of nice-to-have technical skills.
6. soft_skills: A list of non-technical attributes (e.g. Communication, Teamwork, Critical Thinking).
7. minimum_cgpa: The minimum CGPA required on a 10.0 scale. If a percentage is given (e.g. 75%), convert it to a 10-point scale (7.5). If no CGPA is mentioned, set it to 0.0.
8. overall_confidence, skill_confidence, role_confidence, cgpa_confidence: Float scores between 0.0 and 1.0 indicating how clear the information was in the text.
9. explainability_section: Quotes from the text indicating where you found the title, skills, and CGPA.

Strictly adhere to the JSON format. Do not return any other text besides the JSON block.
"""

FEW_SHOT_EXAMPLES = [
    # Example 1: Cloud Backend Engineer
    {
        "input": """
        Title: Junior Cloud Backend Engineer
        Company: CloudTech Solutions
        We are seeking a Backend Developer with 1-2 years of experience. You will build APIs using Node JS and Express. 
        Knowledge of SQL databases like MySQL is mandatory. Docker experience is preferred.
        Candidates must have a minimum CGPA of 7.5. Good problem-solving and communication are required.
        """,
        "output": {
            "role_title": "Junior Cloud Backend Engineer",
            "role_category": "Software Engineering",
            "experience_level": "Junior",
            "required_skills": ["Node.js", "Express", "MySQL", "SQL"],
            "preferred_skills": ["Docker"],
            "soft_skills": ["Problem-solving", "Communication"],
            "minimum_cgpa": 7.5,
            "overall_confidence": 0.95,
            "skill_confidence": 0.95,
            "role_confidence": 1.0,
            "cgpa_confidence": 1.0,
            "explainability_section": {
                "role_evidence": "We are seeking a Backend Developer with 1-2 years of experience.",
                "skill_evidence": [
                    {"skill_tag": "Node.js", "evidence_sentence": "You will build APIs using Node JS and Express."},
                    {"skill_tag": "Express", "evidence_sentence": "You will build APIs using Node JS and Express."},
                    {"skill_tag": "MySQL", "evidence_sentence": "Knowledge of SQL databases like MySQL is mandatory."},
                    {"skill_tag": "Docker", "evidence_sentence": "Docker experience is preferred."}
                ],
                "cgpa_evidence": "Candidates must have a minimum CGPA of 7.5."
            }
        }
    },
    # Example 2: Frontend Developer
    {
        "input": """
        Position: Entry Level Frontend Developer
        We are looking for a creative developer to build user interfaces. Core requirements are ReactJS and CSS. 
        Experience with TypeScript is a plus. Candidates should possess strong collaboration skills. GPA requirement: 7.0 minimum.
        """,
        "output": {
            "role_title": "Entry Level Frontend Developer",
            "role_category": "Software Engineering",
            "experience_level": "Entry Level",
            "required_skills": ["React", "CSS"],
            "preferred_skills": ["TypeScript"],
            "soft_skills": ["Collaboration", "Creativity"],
            "minimum_cgpa": 7.0,
            "overall_confidence": 0.90,
            "skill_confidence": 0.90,
            "role_confidence": 1.0,
            "cgpa_confidence": 1.0,
            "explainability_section": {
                "role_evidence": "Position: Entry Level Frontend Developer",
                "skill_evidence": [
                    {"skill_tag": "React", "evidence_sentence": "Core requirements are ReactJS and CSS."},
                    {"skill_tag": "CSS", "evidence_sentence": "Core requirements are ReactJS and CSS."},
                    {"skill_tag": "TypeScript", "evidence_sentence": "Experience with TypeScript is a plus."}
                ],
                "cgpa_evidence": "GPA requirement: 7.0 minimum."
            }
        }
    },
    # Example 3: Data Analyst
    {
        "input": """
        Data Analyst (Internship)
        We are looking for an intern to join our analytics team. You will query databases using SQL, build reports in Tableau. 
        Python scripting experience is preferred. Strong critical thinking is required. No CGPA cut-off.
        """,
        "output": {
            "role_title": "Data Analyst (Internship)",
            "role_category": "Data & Analytics",
            "experience_level": "Internship",
            "required_skills": ["SQL", "Tableau"],
            "preferred_skills": ["Python"],
            "soft_skills": ["Critical thinking"],
            "minimum_cgpa": 0.0,
            "overall_confidence": 0.85,
            "skill_confidence": 0.90,
            "role_confidence": 0.95,
            "cgpa_confidence": 0.80,
            "explainability_section": {
                "role_evidence": "Data Analyst (Internship)",
                "skill_evidence": [
                    {"skill_tag": "SQL", "evidence_sentence": "You will query databases using SQL, build reports in Tableau."},
                    {"skill_tag": "Tableau", "evidence_sentence": "You will query databases using SQL, build reports in Tableau."},
                    {"skill_tag": "Python", "evidence_sentence": "Python scripting experience is preferred."}
                ],
                "cgpa_evidence": "No CGPA cut-off."
            }
        }
    },
    # Example 4: AI Engineer
    {
        "input": """
        AI Engineer - Mid Level
        We are seeking a Mid-level Machine Learning specialist. Required: Python, PyTorch, and NLP. 
        Preferred: Docker and Kubernetes. We require a minimum grade of 80% (equivalent to 8.0 CGPA). 
        Must display leadership skills.
        """,
        "output": {
            "role_title": "AI Engineer - Mid Level",
            "role_category": "AI/ML",
            "experience_level": "Mid Level",
            "required_skills": ["Python", "PyTorch", "NLP"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "soft_skills": ["Leadership"],
            "minimum_cgpa": 8.0,
            "overall_confidence": 0.90,
            "skill_confidence": 0.90,
            "role_confidence": 1.0,
            "cgpa_confidence": 0.90,
            "explainability_section": {
                "role_evidence": "AI Engineer - Mid Level",
                "skill_evidence": [
                    {"skill_tag": "Python", "evidence_sentence": "Required: Python, PyTorch, and NLP."},
                    {"skill_tag": "PyTorch", "evidence_sentence": "Required: Python, PyTorch, and NLP."},
                    {"skill_tag": "NLP", "evidence_sentence": "Required: Python, PyTorch, and NLP."},
                    {"skill_tag": "Docker", "evidence_sentence": "Preferred: Docker and Kubernetes."},
                    {"skill_tag": "Kubernetes", "evidence_sentence": "Preferred: Docker and Kubernetes."}
                ],
                "cgpa_evidence": "We require a minimum grade of 80% (equivalent to 8.0 CGPA)."
            }
        }
    }
]
