// Centralized API Service Layer

import axios from 'axios';
import { PlacementAnalysisResult, AIStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log("API_BASE_URL =", API_BASE_URL);
const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Performs health check against backend
   */
  async healthCheck(): Promise<{ status: string; pipeline_version: string }> {
    const response = await client.get('/health');
    return response.data;
  },

  /**
   * Retrieves real-time Gemini API status
   */
  async getAIStatus(): Promise<AIStatus> {
    const response = await client.get('/api/v1/ai-status');
    return response.data;
  },

  /**
   * Invokes full-analysis pipeline with resume text and job description
   */
  async runFullAnalysis(
    studentId: string,
    resumeText: string,
    jobId: string,
    jobDescription: string
  ): Promise<PlacementAnalysisResult> {
    const response = await client.post('/api/v1/full-analysis', {
      student_id: studentId,
      resume_text: resumeText,
      job_id: jobId,
      job_description: jobDescription,
    });
    return response.data;
  },
};
