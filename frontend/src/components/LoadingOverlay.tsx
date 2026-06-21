// Loading Overlay Component

import React from 'react';

interface LoadingOverlayProps {
  message: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ message }) => {
  return (
    <div style={containerStyle}>
      <div className="spinner"></div>
      <p style={textStyle}>{message}</p>
    </div>
  );
};

const containerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '40px',
  width: '100%',
  minHeight: '300px',
};

const textStyle: React.CSSProperties = {
  fontSize: '1.1rem',
  fontWeight: 500,
  color: 'var(--text-secondary)',
};
