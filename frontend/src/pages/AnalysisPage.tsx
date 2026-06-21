// Analysis / Loading Progress Page Component

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../context/AnalysisContext';
import { ErrorBanner } from '../components/ErrorBanner';

const STEPS = [
  "Parsing Uploaded Resume PDF",
  "Extracting Student Profile Skills & Projects",
  "Analyzing Job Description Requirements",
  "Computing Matching Score & CGPA Eligibility",
  "Generating Skill Gap Recommendations",
  "Building Multi-week Career Roadmap",
  "Structuring Interview Readiness Pack",
];

export const AnalysisPage: React.FC = () => {
  const { loading, error, analysisResult, resetAnalysis } = useAnalysis();
  const [activeStepIdx, setActiveStepIdx] = useState<number>(0);
  const navigate = useNavigate();

  // Redirect to results immediately once loaded successfully
  useEffect(() => {
    if (!loading && analysisResult) {
      navigate('/results');
    }
  }, [loading, analysisResult, navigate]);

  // Simulate progressive step increments to keep user engaged during loading
  useEffect(() => {
    if (!loading) return;

    const interval = setInterval(() => {
      setActiveStepIdx(prev => {
        // Ticks through steps sequentially but slows down near completion
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 900);

    return () => clearInterval(interval);
  }, [loading]);

  const handleBack = () => {
    resetAnalysis();
    navigate('/');
  };

  return (
    <div style={containerStyle}>
      {error ? (
        <div style={errorWrapperStyle}>
          <ErrorBanner message={error} onRetry={handleBack} />
        </div>
      ) : (
        <div className="glass-card" style={cardStyle}>
          <div className="spinner"></div>
          <h2 className="glow-text-indigo" style={headerStyle}>Running Placement Analysis</h2>
          <p style={subTextStyle}>Please wait. Our agents are analyzing the fit profiles...</p>

          <div className="stepper">
            {STEPS.map((step, idx) => {
              const isCompleted = idx < activeStepIdx;
              const isActive = idx === activeStepIdx;
              return (
                <div 
                  key={idx} 
                  className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                >
                  <div className="step-indicator">
                    {isCompleted ? '✓' : idx + 1}
                  </div>
                  <span>{step}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

const containerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '60vh',
  width: '100%',
};

const errorWrapperStyle: React.CSSProperties = {
  width: '100%',
  display: 'flex',
  justifyContent: 'center',
};

const cardStyle: React.CSSProperties = {
  maxWidth: '600px',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: '40px 30px',
};

const headerStyle: React.CSSProperties = {
  fontSize: '1.6rem',
  marginBottom: '8px',
  textAlign: 'center',
};

const subTextStyle: React.CSSProperties = {
  color: 'var(--text-secondary)',
  fontSize: '0.95rem',
  marginBottom: '30px',
  textAlign: 'center',
};
