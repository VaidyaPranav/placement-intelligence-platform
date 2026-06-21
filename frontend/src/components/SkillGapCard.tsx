// Skill Gap Card Component

import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { SkillGapReport, MatchResult } from '../types';

interface SkillGapCardProps {
  gapReport: SkillGapReport;
  matchResult: MatchResult;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({ gapReport, matchResult }) => {
  // Count counts
  const matchedReq = matchResult.matched_skills.length;
  const missingReq = matchResult.missing_skills.length;
  const matchedPref = matchResult.preferred_skills_matched.length;
  const missingPref = matchResult.preferred_skills_missing.length;

  const barData = [
    {
      name: 'Required Skills',
      Matched: matchedReq,
      Missing: missingReq,
    },
    {
      name: 'Preferred Skills',
      Matched: matchedPref,
      Missing: missingPref,
    },
  ];

  // Map severity to colors
  const getSeverityStyles = (sev: string) => {
    switch (sev) {
      case 'LOW':
        return { color: 'var(--color-success)', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.3)' };
      case 'MEDIUM':
        return { color: 'var(--color-warning)', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.3)' };
      case 'HIGH':
        return { color: 'var(--color-danger)', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)' };
      case 'CRITICAL':
        return { color: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)', border: 'rgba(236, 72, 153, 0.3)' };
      default:
        return { color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)', border: 'rgba(99, 102, 241, 0.2)' };
    }
  };

  const sevStyle = getSeverityStyles(gapReport.severity);

  const getPriorityColor = (pri: string) => {
    switch (pri) {
      case 'HIGH':
        return '#f43f5e';
      case 'MEDIUM':
        return '#f59e0b';
      case 'LOW':
        return '#6366f1';
      default:
        return 'var(--text-secondary)';
    }
  };

  return (
    <div className="glass-card" style={cardStyle}>
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Skill Gap Report</h3>

      <div style={flexHeaderStyle}>
        <div>
          <span style={labelStyle}>Gap Score</span>
          <span style={scoreStyle}>{gapReport.gap_score.toFixed(1)}</span>
        </div>
        <div style={sevContainerStyle}>
          <span style={labelStyle}>Severity Level</span>
          <span style={{ 
            ...sevBadgeStyle, 
            color: sevStyle.color, 
            borderColor: sevStyle.border, 
            background: sevStyle.bg 
          }}>
            {gapReport.severity}
          </span>
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Recharts Bar Chart */}
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>Skills Alignment Summary</h4>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} allowDecimals={false} />
            <Tooltip 
              contentStyle={{ background: 'rgba(15, 18, 36, 0.95)', borderColor: 'var(--border-neon)' }}
              labelStyle={{ color: 'var(--text-primary)' }}
            />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
            <Bar dataKey="Matched" fill="var(--color-success)" stackId="a" radius={[0, 0, 0, 0]} />
            <Bar dataKey="Missing" fill="var(--color-danger)" stackId="a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={dividerStyle}></div>

      {/* Recommendations */}
      <div>
        <h4 style={recommendationHeaderStyle}>Actionable Recommendations</h4>
        {gapReport.recommendations && gapReport.recommendations.length > 0 ? (
          <div style={recListStyle}>
            {gapReport.recommendations.map((rec, idx) => {
              const priColor = getPriorityColor(rec.priority);
              return (
                <div key={idx} style={recItemStyle}>
                  <div style={recItemHeaderStyle}>
                    <div style={recTitleBoxStyle}>
                      <span style={{ ...priorityBadgeStyle, background: `${priColor}20`, color: priColor, borderColor: priColor }}>
                        {rec.priority}
                      </span>
                      <strong>{rec.skill}</strong>
                    </div>
                    <span style={estScoreStyle}>
                      Improvement: +{rec.estimated_improvement_score.toFixed(1)}%
                    </span>
                  </div>
                  <p style={recDescStyle}>{rec.recommendation}</p>
                </div>
              );
            })}
          </div>
        ) : (
          <span style={emptyTextStyle}>No recommendations. All skills matched!</span>
        )}
      </div>
    </div>
  );
};

const cardStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const sectionTitleStyle: React.CSSProperties = {
  marginBottom: '20px',
  fontSize: '1.4rem',
};

const flexHeaderStyle: React.CSSProperties = {
  display: 'flex',
  gap: '40px',
  alignItems: 'center',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  display: 'block',
  marginBottom: '4px',
};

const scoreStyle: React.CSSProperties = {
  fontSize: '2.2rem',
  fontWeight: 800,
  fontFamily: 'Outfit, sans-serif',
};

const sevContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const sevBadgeStyle: React.CSSProperties = {
  fontSize: '1.1rem',
  fontWeight: 700,
  padding: '6px 20px',
  borderRadius: '8px',
  border: '1px solid',
  textAlign: 'center',
  fontFamily: 'Outfit, sans-serif',
};

const dividerStyle: React.CSSProperties = {
  height: '1px',
  background: 'rgba(255, 255, 255, 0.05)',
  margin: '20px 0',
};

const chartContainerStyle: React.CSSProperties = {
  background: 'rgba(255,255,255,0.01)',
  border: '1px solid rgba(255, 255, 255, 0.03)',
  borderRadius: '12px',
  padding: '16px',
};

const chartTitleStyle: React.CSSProperties = {
  fontSize: '0.9rem',
  color: 'var(--text-secondary)',
  marginBottom: '12px',
  fontWeight: 600,
  textAlign: 'center',
};

const recommendationHeaderStyle: React.CSSProperties = {
  fontSize: '1rem',
  color: 'var(--text-primary)',
  marginBottom: '16px',
  fontWeight: 600,
};

const recListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

const recItemStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  padding: '16px',
};

const recItemHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px',
  flexWrap: 'wrap',
  gap: '8px',
};

const recTitleBoxStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  fontSize: '1rem',
};

const priorityBadgeStyle: React.CSSProperties = {
  fontSize: '0.7rem',
  fontWeight: 700,
  padding: '2px 8px',
  borderRadius: '4px',
  border: '1px solid',
};

const estScoreStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  fontWeight: 600,
  color: 'var(--color-info)',
};

const recDescStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.5,
};

const emptyTextStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-muted)',
  fontStyle: 'italic',
};
