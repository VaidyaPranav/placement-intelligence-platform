// Analysis Context Provider

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { extractTextFromPDF } from '../services/pdfExtractor';
import { PlacementAnalysisResult } from '../types';

export type BackendStatusType = 'CONNECTING' | 'ONLINE' | 'OFFLINE';

interface AnalysisContextProps {
  analysisResult: PlacementAnalysisResult | null;
  loading: boolean;
  error: string | null;
  backendStatus: BackendStatusType;
  checkBackend: () => Promise<void>;
  triggerAnalysis: (resumeFile: File, jobDescription: string) => Promise<void>;
  resetAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextProps | undefined>(undefined);

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [analysisResult, setAnalysisResult] = useState<PlacementAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<BackendStatusType>('CONNECTING');

  const checkBackend = async () => {
    setBackendStatus('CONNECTING');
    try {
      const response = await api.healthCheck();
      if (response && response.status === 'healthy') {
        setBackendStatus('ONLINE');
      } else {
        setBackendStatus('OFFLINE');
      }
    } catch (err) {
      console.error("[BACKEND CONNECTION ERROR]", err);
      setBackendStatus('OFFLINE');
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  const triggerAnalysis = async (resumeFile: File, jobDescription: string) => {
    setLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      // Step 1: Extract PDF Text client-side
      const resumeText = await extractTextFromPDF(resumeFile);

      // Step 2: Auto-generate UUIDs internally
      const studentId = crypto.randomUUID();
      const jobId = crypto.randomUUID();

      // Step 3: Run Full Pipeline Analysis via Centralized API Service
      const result = await api.runFullAnalysis(studentId, resumeText, jobId, jobDescription);
      setAnalysisResult(result);
    } catch (err: any) {
      console.error("[PIPELINE ANALYSIS ERROR]", err);
      let errMsg = "An unexpected error occurred during analysis.";
      if (err.response) {
        // Backend returned error response (e.g. 400 / 500)
        errMsg = err.response.data?.detail || err.response.data?.message || `Server returned error status code: ${err.response.status}`;
      } else if (err.request) {
        // Request made but no response (Backend offline/unreachable)
        errMsg = "Backend server is unreachable. Please check if the API is running and try again.";
      } else {
        errMsg = err.message || errMsg;
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setAnalysisResult(null);
    setError(null);
    setLoading(false);
  };

  return (
    <AnalysisContext.Provider
      value={{
        analysisResult,
        loading,
        error,
        backendStatus,
        checkBackend,
        triggerAnalysis,
        resetAnalysis,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};
