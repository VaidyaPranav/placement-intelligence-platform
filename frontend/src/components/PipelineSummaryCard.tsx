// Pipeline Summary Card Component

import React from 'react';
import { PlacementAnalysisResult } from '../types';

interface PipelineSummaryCardProps {
  result: PlacementAnalysisResult;
}

export const PipelineSummaryCard: React.FC<PipelineSummaryCardProps> = ({ result }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'var(--color-success)';
      case 'PARTIAL_SUCCESS':
        return 'var(--color-warning)';
      case 'FAILED':
        return 'var(--color-danger)';
      default:
        return 'var(--text-secondary)';
    }
  };

  const statusColor = getStatusColor(result.pipeline_status);

  return (
    <div className="glass-card">
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Pipeline Summary</h3>

      <div style={metaGridStyle}>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Pipeline Status</span>
          <span style={{ ...valueStyle, color: statusColor }}>
            {result.pipeline_status.replace('_', ' ')}
          </span>
        </div>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Total Execution Time</span>
          <span style={valueStyle}>{result.total_execution_time_seconds.toFixed(2)} seconds</span>
        </div>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Pipeline Version</span>
          <span style={valueStyle}>{result.pipeline_version}</span>
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Completed steps */}
      <div style={stepBlockStyle}>
        <h4 style={subTitleStyle}>Completed Phases ({result.execution_steps_completed.length}/6)</h4>
        <div style={stepListStyle}>
          {result.execution_steps_completed.map((step, idx) => (
            <div key={idx} style={stepItemStyle}>
              <span style={successIndicatorStyle}>✓</span>
              <span>{step}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Failed/Skipped steps */}
      {result.execution_steps_failed && result.execution_steps_failed.length > 0 && (
        <div style={stepBlockStyle}>
          <h4 style={{ ...subTitleStyle, color: 'var(--color-warning)' }}>
            Failed/Skipped Phases ({result.execution_steps_failed.length}/6)
          </h4>
          <div style={stepListStyle}>
            {result.execution_steps_failed.map((step, idx) => (
              <div key={idx} style={stepItemStyle}>
                <span style={failIndicatorStyle}>✗</span>
                <span style={{ color: 'var(--text-muted)' }}>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pipeline warnings/errors */}
      {result.errors && result.errors.length > 0 && (
        <div style={errorBlockStyle}>
          <h4 style={errorTitleStyle}>Logged Errors & Warnings</h4>
          <div style={errorListStyle}>
            {result.errors.map((err, idx) => (
              <div key={idx} style={errorItemStyle}>
                • {err}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const sectionTitleStyle: React.CSSProperties = {
  marginBottom: '20px',
  fontSize: '1.4rem',
};

const metaGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(3, 1fr)',
  gap: '16px',
};

const metaItemStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const valueStyle: React.CSSProperties = {
  fontSize: '1.1rem',
  fontWeight: 600,
};

const dividerStyle: React.CSSProperties = {
  height: '1px',
  background: 'rgba(255, 255, 255, 0.05)',
  margin: '20px 0',
};

const stepBlockStyle: React.CSSProperties = {
  marginBottom: '20px',
};

const subTitleStyle: React.CSSProperties = {
  fontSize: '0.95rem',
  marginBottom: '10px',
  color: 'var(--text-secondary)',
  fontWeight: 600,
};

const stepListStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '12px',
};

const stepItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '0.85rem',
  background: 'rgba(255, 255, 255, 0.02)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '20px',
  padding: '4px 12px',
};

const successIndicatorStyle: React.CSSProperties = {
  color: 'var(--color-success)',
  fontWeight: 'bold',
};

const failIndicatorStyle: React.CSSProperties = {
  color: 'var(--color-danger)',
  fontWeight: 'bold',
};

const errorBlockStyle: React.CSSProperties = {
  background: 'rgba(239, 68, 68, 0.03)',
  border: '1px solid rgba(239, 68, 68, 0.1)',
  borderRadius: '8px',
  padding: '16px',
  marginTop: '20px',
};

const errorTitleStyle: React.CSSProperties = {
  fontSize: '0.9rem',
  color: 'var(--color-danger)',
  marginBottom: '10px',
  fontWeight: 600,
};

const errorListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const errorItemStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.4,
};
