# Prompt Instructions and Few-Shot Examples for Student Intelligence Agent

SYSTEM_INSTRUCTION = """
You are a precision Student Intelligence Agent. Your job is to convert unstructured student resume text into a structured StudentProfile object.

You must extract the following fields and return them as a valid JSON object matching the requested schema:
1. name: The full name of the student.
2. department: Must match one of these specific institutional departments based on major:
   - "CS" (Computer Science, Computer Science & Engineering)
   - "IT" (Information Technology)
   - "ECE" (Electronics & Communication Engineering)
   - "EE" (Electrical Engineering)
   - "ME" (Mechanical Engineering)
3. cgpa: The CGPA of the student on a 10.0 scale. If scaled out of 4.0 or 100%, convert it to a 10.0 scale (e.g. 3.6/4.0 -> 9.0; 85% -> 8.5). If not found, set to 0.0.
4. skills: List of unique technical skills. Normalize standard tech keywords:
   - ReactJS or React.js -> "React"
   - NodeJS or Node -> "Node.js"
   - My SQL -> "MySQL"
   - Tensor Flow -> "TensorFlow"
   - PowerBI -> "Power BI"
5. projects: List of projects, each having a "title" and a "complexity_score" (integer 1-10). Assign score brackets as follows:
   - Simple CRUD App -> 3-4
   - Full Stack App -> 5-7
   - Cloud Deployment / Infrastructure -> 7-8
   - AI/ML/DL Project -> 8-10
6. certifications: List of certifications, each having "name" and "issuer".
7. achievements: List of strings detailing honors, competitive coding ranks, or extracurricular successes.
8. internships: List of internships, each having "company", "role", and "duration_months" (minimum 1).
9. resume_text: The exact raw text of the resume that you parsed.
10. resume_confidence, overall_confidence: Float scores between 0.0 and 1.0 indicating parsing clarity.
11. verified_sources: Set to ["RESUME_PDF"].
12. github_analysis: An object with:
    - "repo_count": 0
    - "languages": []
    - "verification_status": "UNVERIFIED"
13. technical_score, project_score, communication_score, interview_score, certification_score: Set to 0.
14. placement_status: Set to "UNPLACED".
15. target_role_category: Map the student's primary focus to one of the following:
    - "Software Engineering" (default)
    - "Data & Analytics"
    - "AI/ML"
    - "Cloud & DevOps"
16. profile_version: Set to "1.0.0".
17. explainability_section: An object containing:
    - name_evidence: Sentence/line where the student's name is found.
    - department_evidence: Sentence/line indicating their department.
    - cgpa_evidence: Sentence/line showing CGPA.
    - skill_evidence: List of objects with "skill_tag" and "evidence_sentence".
    - project_evidence: List of objects with "project_title" and "evidence_sentence".
    - certification_evidence: List of objects with "certification_name" and "evidence_sentence".
    - internship_evidence: List of objects with "internship_company" and "evidence_sentence".
18. created_at, updated_at: Current timestamp (ISO 8601 UTC format).
19. github_url, portfolio_url, linkedin_url: Optional URIs if found in the text.

Strictly adhere to the JSON format. Do not return any other text besides the JSON block.
"""

FEW_SHOT_EXAMPLES = [
    # Example 1: Full Stack Student
    {
        "input": """
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
        - Web Developer Intern at DevCorp (May 2025 - July 2025, 2 months): Developed UI components in React and optimized backend routes.
        """,
        "output": {
            "name": "Varun Sharma",
            "department": "CS",
            "cgpa": 8.5,
            "skills": ["React", "Node.js", "JavaScript", "HTML", "CSS", "MySQL", "Git", "Docker"],
            "projects": [
                {"title": "E-Commerce Web App", "complexity_score": 6},
                {"title": "Personal Portfolio Site", "complexity_score": 3}
            ],
            "certifications": [
                {"name": "React Developer Certification", "issuer": "Meta"}
            ],
            "achievements": [
                "Secured Rank 450 in Google Kickstart Round D."
            ],
            "internships": [
                {"company": "DevCorp", "role": "Web Developer Intern", "duration_months": 2}
            ],
            "resume_text": "Varun Sharma\nEmail: varun@example.com | GitHub: https://github.com/varunsharma | LinkedIn: https://linkedin.com/in/varunsharma\nB.Tech in Computer Science and Engineering\nCGPA: 8.5/10.0\n\nSkills: ReactJS, NodeJS, JavaScript, HTML, CSS, My SQL, Git, Docker\n\nProjects:\n- E-Commerce Web App: Built a full stack online store using React.js and NodeJS. Implemented MySQL database integration.\n- Personal Portfolio Site: A simple React site displaying my details.\n\nCertifications:\n- React Developer Certification issued by Meta\n\nAchievements:\n- Secured Rank 450 in Google Kickstart Round D.\n\nInternships:\n- Web Developer Intern at DevCorp (May 2025 - July 2025, 2 months): Developed UI components in React and optimized backend routes.",
            "resume_confidence": 0.95,
            "verified_sources": ["RESUME_PDF"],
            "github_analysis": {
                "repo_count": 0,
                "languages": [],
                "verification_status": "UNVERIFIED"
            },
            "technical_score": 0,
            "project_score": 0,
            "communication_score": 0,
            "interview_score": 0,
            "certification_score": 0,
            "placement_status": "UNPLACED",
            "target_role_category": "Software Engineering",
            "profile_version": "1.0.0",
            "overall_confidence": 0.95,
            "explainability_section": {
                "name_evidence": "Varun Sharma",
                "department_evidence": "B.Tech in Computer Science and Engineering",
                "cgpa_evidence": "CGPA: 8.5/10.0",
                "skill_evidence": [
                    {"skill_tag": "React", "evidence_sentence": "Skills: ReactJS, NodeJS, JavaScript, HTML, CSS, My SQL, Git, Docker"},
                    {"skill_tag": "Node.js", "evidence_sentence": "Skills: ReactJS, NodeJS, JavaScript, HTML, CSS, My SQL, Git, Docker"},
                    {"skill_tag": "MySQL", "evidence_sentence": "Skills: ReactJS, NodeJS, JavaScript, HTML, CSS, My SQL, Git, Docker"}
                ],
                "project_evidence": [
                    {"project_title": "E-Commerce Web App", "evidence_sentence": "- E-Commerce Web App: Built a full stack online store using React.js and NodeJS. Implemented MySQL database integration."},
                    {"project_title": "Personal Portfolio Site", "evidence_sentence": "- Personal Portfolio Site: A simple React site displaying my details."}
                ],
                "certification_evidence": [
                    {"certification_name": "React Developer Certification", "evidence_sentence": "- React Developer Certification issued by Meta"}
                ],
                "internship_evidence": [
                    {"internship_company": "DevCorp", "evidence_sentence": "- Web Developer Intern at DevCorp (May 2025 - July 2025, 2 months): Developed UI components in React and optimized backend routes."}
                ]
            },
            "created_at": "2026-06-21T00:00:00Z",
            "updated_at": "2026-06-21T00:00:00Z",
            "github_url": "https://github.com/varunsharma",
            "portfolio_url": None,
            "linkedin_url": "https://linkedin.com/in/varunsharma"
        }
    },
    # Example 2: Cloud Student
    {
        "input": """
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
        - DevOps Intern at CloudScale Inc (June 2025 - August 2025, 3 months): Automated CI/CD pipelines using Gitlab and Docker.
        """,
        "output": {
            "name": "Aditya Sen",
            "department": "IT",
            "cgpa": 9.1,
            "skills": ["AWS", "Terraform", "Docker", "Python", "Bash", "Kubernetes", "Linux"],
            "projects": [
                {"title": "Terraform Multi-AZ Setup", "complexity_score": 8},
                {"title": "Dockerized Microservices", "complexity_score": 7}
            ],
            "certifications": [
                {"name": "AWS Certified Solutions Architect Associate", "issuer": "Amazon Web Services"}
            ],
            "achievements": [
                "Certified AWS Solutions Architect."
            ],
            "internships": [
                {"company": "CloudScale Inc", "role": "DevOps Intern", "duration_months": 3}
            ],
            "resume_text": "Aditya Sen\nEmail: aditya.sen@example.com | GitHub: https://github.com/adityasen\nB.Tech in Information Technology\nCGPA: 9.1/10\n\nSkills: AWS, Terraform, Docker, Python, Bash, Kubernetes, Linux\n\nProjects:\n- Terraform Multi-AZ Setup: Orchestrated and deployed a highly-available VPC infrastructure on AWS using Terraform.\n- Dockerized Microservices: Containerized and deployed Python applications using Docker and Kubernetes.\n\nCertifications:\n- AWS Certified Solutions Architect Associate issued by Amazon Web Services\n\nAchievements:\n- Certified AWS Solutions Architect.\n\nInternships:\n- DevOps Intern at CloudScale Inc (June 2025 - August 2025, 3 months): Automated CI/CD pipelines using Gitlab and Docker.",
            "resume_confidence": 0.96,
            "verified_sources": ["RESUME_PDF"],
            "github_analysis": {
                "repo_count": 0,
                "languages": [],
                "verification_status": "UNVERIFIED"
            },
            "technical_score": 0,
            "project_score": 0,
            "communication_score": 0,
            "interview_score": 0,
            "certification_score": 0,
            "placement_status": "UNPLACED",
            "target_role_category": "Cloud & DevOps",
            "profile_version": "1.0.0",
            "overall_confidence": 0.96,
            "explainability_section": {
                "name_evidence": "Aditya Sen",
                "department_evidence": "B.Tech in Information Technology",
                "cgpa_evidence": "CGPA: 9.1/10",
                "skill_evidence": [
                    {"skill_tag": "AWS", "evidence_sentence": "Skills: AWS, Terraform, Docker, Python, Bash, Kubernetes, Linux"},
                    {"skill_tag": "Terraform", "evidence_sentence": "Skills: AWS, Terraform, Docker, Python, Bash, Kubernetes, Linux"}
                ],
                "project_evidence": [
                    {"project_title": "Terraform Multi-AZ Setup", "evidence_sentence": "- Terraform Multi-AZ Setup: Orchestrated and deployed a highly-available VPC infrastructure on AWS using Terraform."},
                    {"project_title": "Dockerized Microservices", "evidence_sentence": "- Dockerized Microservices: Containerized and deployed Python applications using Docker and Kubernetes."}
                ],
                "certification_evidence": [
                    {"certification_name": "AWS Certified Solutions Architect Associate", "evidence_sentence": "- AWS Certified Solutions Architect Associate issued by Amazon Web Services"}
                ],
                "internship_evidence": [
                    {"internship_company": "CloudScale Inc", "evidence_sentence": "- DevOps Intern at CloudScale Inc (June 2025 - August 2025, 3 months): Automated CI/CD pipelines using Gitlab and Docker."}
                ]
            },
            "created_at": "2026-06-21T00:00:00Z",
            "updated_at": "2026-06-21T00:00:00Z",
            "github_url": "https://github.com/adityasen",
            "portfolio_url": None,
            "linkedin_url": None
        }
    },
    # Example 3: AI Student
    {
        "input": """
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
        - ML Research Intern at VisionLabs (May 2025 - October 2025, 5 months): Trained convolutional neural networks on proprietary datasets.
        """,
        "output": {
            "name": "Priya Patel",
            "department": "ECE",
            "cgpa": 8.8,
            "skills": ["Python", "PyTorch", "TensorFlow", "Computer Vision", "OpenCV", "NumPy", "C++"],
            "projects": [
                {"title": "ResNet Custom Classifier", "complexity_score": 9},
                {"title": "Face Detection App", "complexity_score": 4}
            ],
            "certifications": [
                {"name": "Deep Learning Specialization", "issuer": "Coursera DeepLearning.AI"}
            ],
            "achievements": [
                "Published research paper on Computer Vision in IEEE."
            ],
            "internships": [
                {"company": "VisionLabs", "role": "ML Research Intern", "duration_months": 5}
            ],
            "resume_text": "Priya Patel\nEmail: priya@example.com | LinkedIn: https://linkedin.com/in/priyapatel\nB.Tech in Electronics & Communication Engineering\nCGPA: 8.8/10\n\nSkills: Python, PyTorch, Tensor Flow, Computer Vision, OpenCV, NumPy, C++\n\nProjects:\n- ResNet Custom Classifier: Implemented a deep learning model in PyTorch to classify medical scan images with 94% accuracy.\n- Face Detection App: A real-time face detection system using OpenCV and Python.\n\nCertifications:\n- Deep Learning Specialization issued by Coursera DeepLearning.AI\n\nAchievements:\n- Published research paper on Computer Vision in IEEE.\n\nInternships:\n- ML Research Intern at VisionLabs (May 2025 - October 2025, 5 months): Trained convolutional neural networks on proprietary datasets.",
            "resume_confidence": 0.94,
            "verified_sources": ["RESUME_PDF"],
            "github_analysis": {
                "repo_count": 0,
                "languages": [],
                "verification_status": "UNVERIFIED"
            },
            "technical_score": 0,
            "project_score": 0,
            "communication_score": 0,
            "interview_score": 0,
            "certification_score": 0,
            "placement_status": "UNPLACED",
            "target_role_category": "AI/ML",
            "profile_version": "1.0.0",
            "overall_confidence": 0.94,
            "explainability_section": {
                "name_evidence": "Priya Patel",
                "department_evidence": "B.Tech in Electronics & Communication Engineering",
                "cgpa_evidence": "CGPA: 8.8/10",
                "skill_evidence": [
                    {"skill_tag": "Python", "evidence_sentence": "Skills: Python, PyTorch, Tensor Flow, Computer Vision, OpenCV, NumPy, C++"},
                    {"skill_tag": "TensorFlow", "evidence_sentence": "Skills: Python, PyTorch, Tensor Flow, Computer Vision, OpenCV, NumPy, C++"}
                ],
                "project_evidence": [
                    {"project_title": "ResNet Custom Classifier", "evidence_sentence": "- ResNet Custom Classifier: Implemented a deep learning model in PyTorch to classify medical scan images with 94% accuracy."},
                    {"project_title": "Face Detection App", "evidence_sentence": "- Face Detection App: A real-time face detection system using OpenCV and Python."}
                ],
                "certification_evidence": [
                    {"certification_name": "Deep Learning Specialization", "evidence_sentence": "- Deep Learning Specialization issued by Coursera DeepLearning.AI"}
                ],
                "internship_evidence": [
                    {"internship_company": "VisionLabs", "evidence_sentence": "- ML Research Intern at VisionLabs (May 2025 - October 2025, 5 months): Trained convolutional neural networks on proprietary datasets."}
                ]
            },
            "created_at": "2026-06-21T00:00:00Z",
            "updated_at": "2026-06-21T00:00:00Z",
            "github_url": None,
            "portfolio_url": None,
            "linkedin_url": "https://linkedin.com/in/priyapatel"
        }
    },
    # Example 4: Data Analyst Student
    {
        "input": """
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
        - Data Analyst Intern at RetailCorp (June 2025 - August 2025, 2 months): Developed ETL scripts and built automated reports.
        """,
        "output": {
            "name": "Kunal Shah",
            "department": "IT",
            "cgpa": 8.2,
            "skills": ["SQL", "Power BI", "Tableau", "Python", "Excel", "Pandas", "Matplotlib"],
            "projects": [
                {"title": "Sales Performance Dashboard", "complexity_score": 4},
                {"title": "HR Churn Analysis", "complexity_score": 5}
            ],
            "certifications": [
                {"name": "Microsoft Certified: Power BI Data Analyst Associate", "issuer": "Microsoft"}
            ],
            "achievements": [
                "Winner of university hackathon (Data Analytics track)."
            ],
            "internships": [
                {"company": "RetailCorp", "role": "Data Analyst Intern", "duration_months": 2}
            ],
            "resume_text": "Kunal Shah\nEmail: kunal@example.com | Portfolio: https://kunalshah.dev\nB.Tech in Information Technology\nCGPA: 8.2/10\n\nSkills: SQL, PowerBI, Tableau, Python, Excel, Pandas, Matplotlib\n\nProjects:\n- Sales Performance Dashboard: Created an interactive corporate sales dashboard using PowerBI.\n- HR Churn Analysis: Utilized Python, Pandas, and Matplotlib to analyze employee attrition factors.\n\nCertifications:\n- Microsoft Certified: Power BI Data Analyst Associate issued by Microsoft\n\nAchievements:\n- Winner of university hackathon (Data Analytics track).\n\nInternships:\n- Data Analyst Intern at RetailCorp (June 2025 - August 2025, 2 months): Developed ETL scripts and built automated reports.",
            "resume_confidence": 0.92,
            "verified_sources": ["RESUME_PDF"],
            "github_analysis": {
                "repo_count": 0,
                "languages": [],
                "verification_status": "UNVERIFIED"
            },
            "technical_score": 0,
            "project_score": 0,
            "communication_score": 0,
            "interview_score": 0,
            "certification_score": 0,
            "placement_status": "UNPLACED",
            "target_role_category": "Data & Analytics",
            "profile_version": "1.0.0",
            "overall_confidence": 0.92,
            "explainability_section": {
                "name_evidence": "Kunal Shah",
                "department_evidence": "B.Tech in Information Technology",
                "cgpa_evidence": "CGPA: 8.2/10",
                "skill_evidence": [
                    {"skill_tag": "SQL", "evidence_sentence": "Skills: SQL, PowerBI, Tableau, Python, Excel, Pandas, Matplotlib"},
                    {"skill_tag": "Power BI", "evidence_sentence": "Skills: SQL, PowerBI, Tableau, Python, Excel, Pandas, Matplotlib"}
                ],
                "project_evidence": [
                    {"project_title": "Sales Performance Dashboard", "evidence_sentence": "- Sales Performance Dashboard: Created an interactive corporate sales dashboard using PowerBI."},
                    {"project_title": "HR Churn Analysis", "evidence_sentence": "- HR Churn Analysis: Utilized Python, Pandas, and Matplotlib to analyze employee attrition factors."}
                ],
                "certification_evidence": [
                    {"certification_name": "Microsoft Certified: Power BI Data Analyst Associate", "evidence_sentence": "- Microsoft Certified: Power BI Data Analyst Associate issued by Microsoft"}
                ],
                "internship_evidence": [
                    {"internship_company": "RetailCorp", "evidence_sentence": "- Data Analyst Intern at RetailCorp (June 2025 - August 2025, 2 months): Developed ETL scripts and built automated reports."}
                ]
            },
            "created_at": "2026-06-21T00:00:00Z",
            "updated_at": "2026-06-21T00:00:00Z",
            "github_url": None,
            "portfolio_url": "https://kunalshah.dev",
            "linkedin_url": None
        }
    }
]
