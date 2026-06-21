// Home Page Component

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../context/AnalysisContext';

export const HomePage: React.FC = () => {
  const { triggerAnalysis, backendStatus } = useAnalysis();
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState<string>('');
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (uploadedFile: File) => {
    setValidationError(null);
    if (uploadedFile.type !== 'application/pdf') {
      setValidationError("Only PDF resume files are supported.");
      setFile(null);
      return;
    }
    setFile(uploadedFile);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!file) {
      setValidationError("Please upload a PDF resume file.");
      return;
    }

    if (jdText.trim().length < 50) {
      setValidationError("Job description must be at least 50 characters.");
      return;
    }

    // Trigger analysis context and navigate to stepper page
    triggerAnalysis(file, jdText);
    navigate('/analysis');
  };

  const isOffline = backendStatus === 'OFFLINE';

  return (
    <div style={containerStyle}>
      <div style={welcomeHeaderStyle}>
        <h2 style={titleStyle} className="glow-text-indigo">Evaluate Placement Preparedness</h2>
        <p style={subTitleStyle}>
          Upload a student's resume and paste a target job description. Our multi-agent intelligence pipeline 
          will analyze the fit, identify skill gaps, build roadmaps, and generate role-specific interview prep.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card" style={formStyle}>
        <h3 style={formHeaderStyle}>Placement Readiness Inputs</h3>

        {/* PDF File Upload */}
        <div className="form-group">
          <label>Student Resume (PDF)</label>
          <div
            className="file-upload-container"
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              borderColor: dragActive ? '#6366f1' : 'var(--border-neon)',
              background: dragActive ? 'rgba(99, 102, 241, 0.05)' : 'rgba(15, 18, 36, 0.4)',
            }}
          >
            <input
              type="file"
              id="resume-upload"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
              disabled={isOffline}
            />
            <label htmlFor="resume-upload" style={{ cursor: isOffline ? 'not-allowed' : 'pointer', width: '100%' }}>
              <div className="file-upload-icon">📄</div>
              {file ? (
                <div>
                  <div className="file-upload-text" style={{ color: 'var(--color-success)' }}>
                    ✓ {file.name}
                  </div>
                  <div className="file-upload-subtext">Click or drag another file to replace</div>
                </div>
              ) : (
                <div>
                  <div className="file-upload-text">Drag & drop your PDF resume here</div>
                  <div className="file-upload-subtext">or click to browse local files</div>
                </div>
              )}
            </label>
          </div>
        </div>

        {/* Job Description Text Area */}
        <div className="form-group">
          <label htmlFor="job-description">Job Description</label>
          <textarea
            id="job-description"
            className="textarea-input"
            placeholder="Paste the target job description requirements, responsibilities, and qualifications here (minimum 50 characters)..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            disabled={isOffline}
          />
          <div style={counterStyle}>
            {jdText.length} characters (minimum 50 required)
          </div>
        </div>

        {validationError && (
          <div style={errorContainerStyle}>
            {validationError}
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          style={btnStyle}
          disabled={isOffline || !file || jdText.length < 50}
        >
          Analyze Placement Readiness
        </button>
      </form>
    </div>
  );
};

const containerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  width: '100%',
};

const welcomeHeaderStyle: React.CSSProperties = {
  textAlign: 'center',
  maxWidth: '800px',
  marginBottom: '36px',
};

const titleStyle: React.CSSProperties = {
  fontSize: '2.5rem',
  marginBottom: '16px',
};

const subTitleStyle: React.CSSProperties = {
  color: 'var(--text-secondary)',
  lineHeight: 1.6,
  fontSize: '1.05rem',
};

const formStyle: React.CSSProperties = {
  width: '100%',
  maxWidth: '700px',
};

const formHeaderStyle: React.CSSProperties = {
  fontSize: '1.3rem',
  marginBottom: '24px',
  textAlign: 'left',
};

const counterStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-muted)',
  textAlign: 'right',
  marginTop: '4px',
};

const errorContainerStyle: React.CSSProperties = {
  color: 'var(--color-danger)',
  fontSize: '0.9rem',
  fontWeight: 500,
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.2)',
  borderRadius: '6px',
  padding: '10px 14px',
  marginBottom: '20px',
};

const btnStyle: React.CSSProperties = {
  width: '100%',
  padding: '14px',
};
