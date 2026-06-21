// Backend Connectivity Status Component

import React from 'react';
import { useAnalysis } from '../context/AnalysisContext';

export const BackendStatus: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { backendStatus, checkBackend } = useAnalysis();

  if (backendStatus === 'CONNECTING') {
    return (
      <div style={overlayStyle}>
        <div className="glass-card" style={cardStyle}>
          <div className="spinner"></div>
          <h2 className="glow-text-indigo">Establishing Server Connection</h2>
          <p style={textStyle}>Checking backend health status...</p>
        </div>
      </div>
    );
  }

  if (backendStatus === 'OFFLINE') {
    return (
      <div style={overlayStyle}>
        <div className="glass-card" style={{ ...cardStyle, borderColor: 'var(--color-danger)' }}>
          <div style={iconStyle}>⚠️</div>
          <h2 style={{ color: 'var(--color-danger)' }} className="glow-text-cyan">Backend Offline</h2>
          <p style={textStyle}>
            The Placement Intelligence Platform service cannot be reached. 
            Please ensure the FastAPI backend is running.
          </p>
          <div style={bulletBoxStyle}>
            <p><strong>Troubleshooting Checklists:</strong></p>
            <ul style={listStyle}>
              <li>Run <code>uvicorn backend.app.main:app --reload --port 8000</code> in your terminal</li>
              <li>Verify network port configurations & firewall rules</li>
              <li>Confirm VITE_API_BASE_URL is set correctly in .env</li>
            </ul>
          </div>
          <button className="btn btn-primary" onClick={checkBackend}>
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="no-print" style={badgeStyle}>
        <span style={dotStyle}></span>
        Server: Online
      </div>
      {children}
    </>
  );
};

// Component-specific styles
const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: 'rgba(4, 5, 10, 0.95)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 9999,
  padding: '20px',
};

const cardStyle: React.CSSProperties = {
  maxWidth: '550px',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  gap: '20px',
};

const textStyle: React.CSSProperties = {
  color: 'var(--text-secondary)',
  fontSize: '0.95rem',
  lineHeight: 1.5,
};

const iconStyle: React.CSSProperties = {
  fontSize: '3.5rem',
};

const bulletBoxStyle: React.CSSProperties = {
  textAlign: 'left',
  width: '100%',
  background: 'rgba(255, 255, 255, 0.03)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  padding: '16px',
  color: 'var(--text-secondary)',
  fontSize: '0.85rem',
};

const listStyle: React.CSSProperties = {
  paddingLeft: '20px',
  marginTop: '8px',
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const badgeStyle: React.CSSProperties = {
  position: 'absolute',
  top: '20px',
  right: '20px',
  background: 'rgba(16, 185, 129, 0.1)',
  border: '1px solid rgba(16, 185, 129, 0.2)',
  borderRadius: '20px',
  padding: '6px 12px',
  fontSize: '0.8rem',
  fontWeight: 600,
  color: 'var(--color-success)',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const dotStyle: React.CSSProperties = {
  width: '8px',
  height: '8px',
  borderRadius: '50%',
  background: 'var(--color-success)',
  boxShadow: '0 0 8px var(--color-success)',
};
