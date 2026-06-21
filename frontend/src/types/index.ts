// Placement Intelligence Platform Typings

export interface StudentProfile {
  student_id: string;
  name: string;
  department: string;
  cgpa: number;
  skills: string[];
  projects: any[];
  certifications: any[];
  internships: any[];
  resume_text: string;
  resume_confidence: number;
  github_analysis?: any;
  technical_score: number;
  project_score: number;
  communication_score: number;
  interview_score: number;
  placement_status: string;
  target_role_category: string;
  overall_confidence: number;
  created_at?: string;
  updated_at?: string;
  github_url?: string;
  portfolio_url?: string;
  linkedin_url?: string;
  extraction_method?: string;
}

export interface CompanyIntelligenceOutput {
  job_id: string;
  role_title: string;
  role_category: string;
  experience_level: string;
  required_skills: string[];
  preferred_skills: string[];
  soft_skills?: string[];
  minimum_cgpa: number;
  overall_confidence: number;
  extraction_method?: string;
}

export interface MatchResult {
  student_id: string;
  job_id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  preferred_skills_matched: string[];
  preferred_skills_missing: string[];
  cgpa_eligible: boolean;
  recommendation: string;
  reasoning: string;
  overall_confidence: number;
  required_skill_score?: number;
  preferred_skill_score?: number;
  cgpa_score?: number;
}

export interface SkillRecommendation {
  skill: string;
  priority: string;
  recommendation: string;
  estimated_improvement_score: number;
}

export interface SkillGapReport {
  student_id: string;
  job_id: string;
  gap_score: number;
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  severity: string;
  recommendations: SkillRecommendation[];
  overall_confidence: number;
}

export interface RoadmapTask {
  week_number: number;
  skill: string;
  title: string;
  description: string;
  estimated_hours: number;
  difficulty: string;
}

export interface RoadmapWeek {
  week_number: number;
  tasks: RoadmapTask[];
}

export interface CareerRoadmap {
  student_id: string;
  total_weeks: number;
  roadmap_weeks: RoadmapWeek[];
  expected_match_score_improvement: number;
  overall_confidence: number;
  roadmap_version: string;
  generated_from_severity: string;
  roadmap_summary: string;
}

export interface InterviewQuestion {
  question: string;
  skill: string;
  difficulty: string;
  expected_answer_keywords: string[];
  evaluation_rubric: string[];
}

export interface InterviewPreparationReport {
  student_id: string;
  job_id: string;
  role_title: string;
  technical_questions: InterviewQuestion[];
  behavioral_questions: InterviewQuestion[];
  weak_area_questions: InterviewQuestion[];
  strong_area_questions: InterviewQuestion[];
  focus_areas: string[];
  overall_difficulty: string;
  estimated_interview_readiness_score: number;
  overall_confidence: number;
  interview_pack_version: string;
  generated_from_match_score: number;
  preparation_summary: string;
}

export interface PlacementAnalysisResult {
  student_profile: StudentProfile | null;
  hiring_requirements: CompanyIntelligenceOutput | null;
  match_result: MatchResult | null;
  skill_gap_report: SkillGapReport | null;
  career_roadmap: CareerRoadmap | null;
  interview_report: InterviewPreparationReport | null;
  pipeline_status: string;
  errors: string[];
  execution_steps_completed: string[];
  execution_steps_failed: string[];
  total_execution_time_seconds: number;
  pipeline_version: string;
}

export interface AIStatus {
  llm_enrichment_enabled: boolean;
  fallback_enabled: boolean;
  gemini_api_configured: boolean;
  status: 'AI_ACTIVE' | 'FALLBACK_MODE' | 'API_KEY_MISSING';
}
