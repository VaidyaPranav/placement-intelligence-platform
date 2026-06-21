// Error Banner Component

import React from 'react';

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => {
  return (
    <div className="glass-card" style={cardStyle}>
      <div style={headerStyle}>
        <span style={iconStyle}>⚠️</span>
        <h3 style={titleStyle}>Analysis Error</h3>
      </div>
      <p style={messageStyle}>{message}</p>
      {onRetry && (
        <button className="btn btn-secondary" style={btnStyle} onClick={onRetry}>
          Try Again / Back
        </button>
      )}
    </div>
  );
};

const cardStyle: React.CSSProperties = {
  borderColor: 'var(--color-danger)',
  background: 'rgba(239, 68, 68, 0.05)',
  maxWidth: '600px',
  width: '100%',
  margin: '20px auto',
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const iconStyle: React.CSSProperties = {
  fontSize: '1.5rem',
};

const titleStyle: React.CSSProperties = {
  color: 'var(--color-danger)',
  margin: 0,
};

const messageStyle: React.CSSProperties = {
  color: 'var(--text-secondary)',
  fontSize: '0.95rem',
  lineHeight: 1.5,
};

const btnStyle: React.CSSProperties = {
  alignSelf: 'flex-start',
  marginTop: '8px',
};
