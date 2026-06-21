// Match Score Card Component

import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { MatchResult } from '../types';

interface MatchScoreCardProps {
  matchResult: MatchResult;
}

export const MatchScoreCard: React.FC<MatchScoreCardProps> = ({ matchResult }) => {
  const score = matchResult.match_score;

  const totalReq = matchResult.matched_skills.length + matchResult.missing_skills.length;
  const reqScore = matchResult.required_skill_score ?? (totalReq > 0 ? (matchResult.matched_skills.length / totalReq * 100.0) : 100.0);

  const totalPref = matchResult.preferred_skills_matched.length + matchResult.preferred_skills_missing.length;
  const prefScore = matchResult.preferred_skill_score ?? (totalPref > 0 ? (matchResult.preferred_skills_matched.length / totalPref * 100.0) : 100.0);

  const cgpaScore = matchResult.cgpa_score ?? (matchResult.cgpa_eligible ? 100.0 : 0.0);

  // Calculate weighted contributions
  const reqContrib = (reqScore * 0.70);
  const prefContrib = (prefScore * 0.20);
  const cgpaContrib = (cgpaScore * 0.10);
  
  // Map recommendation to colors
  const getRecColor = (rec: string) => {
    switch (rec) {
      case 'STRONG_MATCH':
        return '#10b981'; // Green
      case 'GOOD_MATCH':
        return '#3b82f6'; // Blue
      case 'PARTIAL_MATCH':
        return '#f59e0b'; // Amber
      case 'WEAK_MATCH':
      case 'NOT_ELIGIBLE':
        return '#ef4444'; // Red
      default:
        return '#6366f1';
    }
  };

  const color = getRecColor(matchResult.recommendation);

  // Semi-circle gauge data
  const chartData = [
    { value: score },
    { value: 100 - score },
  ];

  return (
    <div className="glass-card" style={cardStyle}>
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Match Analysis</h3>
      
      <div style={contentLayoutStyle}>
        {/* Recharts Gauge */}
        <div style={gaugeContainerStyle}>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="90%"
                startAngle={180}
                endAngle={0}
                innerRadius={65}
                outerRadius={85}
                paddingAngle={0}
                dataKey="value"
              >
                <Cell fill={color} />
                <Cell fill="rgba(255, 255, 255, 0.05)" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div style={gaugeLabelStyle}>
            <span style={scoreTextStyle}>{score.toFixed(1)}%</span>
            <span style={scoreSubtextStyle}>Match Score</span>
          </div>
        </div>

        {/* Match info */}
        <div style={infoStyle}>
          <div style={recContainerStyle}>
            <span style={recLabelStyle}>Recommendation</span>
            <span style={{ ...recBadgeStyle, background: `${color}20`, borderColor: color, color: color }}>
              {matchResult.recommendation.replace('_', ' ')}
            </span>
          </div>

          <div style={recContainerStyle}>
            <span style={recLabelStyle}>CGPA Eligibility</span>
            <span style={{ 
              ...eligibilityBadgeStyle, 
              color: matchResult.cgpa_eligible ? 'var(--color-success)' : 'var(--color-danger)',
              background: matchResult.cgpa_eligible ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'
            }}>
              {matchResult.cgpa_eligible ? '✓ Eligible' : '✗ Ineligible (Below Minimum)'}
            </span>
          </div>
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Contribution Breakdown */}
      <div style={breakdownSectionStyle}>
        <span style={breakdownLabelStyle}>Score Contribution Breakdown</span>
        <div style={breakdownContainerStyle}>
          {/* Required Skills Contribution */}
          <div style={breakdownItemStyle}>
            <div style={breakdownHeaderStyle}>
              <span>Required Skills Contribution (70% Max)</span>
              <span style={breakdownValueStyle}>{reqContrib.toFixed(1)}% <span style={breakdownSubtextStyle}>({reqScore.toFixed(0)}% base)</span></span>
            </div>
            <div style={progressTrackStyle}>
              <div style={{ ...progressFillStyle, width: `${(reqContrib / 70) * 100}%`, background: color }} />
            </div>
          </div>

          {/* Preferred Skills Contribution */}
          <div style={breakdownItemStyle}>
            <div style={breakdownHeaderStyle}>
              <span>Preferred Skills Contribution (20% Max)</span>
              <span style={breakdownValueStyle}>{prefContrib.toFixed(1)}% <span style={breakdownSubtextStyle}>({prefScore.toFixed(0)}% base)</span></span>
            </div>
            <div style={progressTrackStyle}>
              <div style={{ ...progressFillStyle, width: `${(prefContrib / 20) * 100}%`, background: color }} />
            </div>
          </div>

          {/* CGPA Contribution */}
          <div style={breakdownItemStyle}>
            <div style={breakdownHeaderStyle}>
              <span>CGPA Contribution (10% Max)</span>
              <span style={breakdownValueStyle}>{cgpaContrib.toFixed(1)}% <span style={breakdownSubtextStyle}>({cgpaScore.toFixed(0)}% base)</span></span>
            </div>
            <div style={progressTrackStyle}>
              <div style={{ ...progressFillStyle, width: `${(cgpaContrib / 10) * 100}%`, background: color }} />
            </div>
          </div>
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Skills breakdown */}
      <div style={skillsSectionStyle}>
        <div>
          <h4 style={skillHeaderStyle}>Matched Required Skills</h4>
          {matchResult.matched_skills.length > 0 ? (
            <div style={pillContainerStyle}>
              {matchResult.matched_skills.map((s, i) => (
                <span key={i} style={{ ...pillStyle, color: 'var(--color-success)', borderColor: 'rgba(16, 185, 129, 0.3)', background: 'rgba(16, 185, 129, 0.05)' }}>
                  {s}
                </span>
              ))}
            </div>
          ) : (
            <span style={emptyTextStyle}>None</span>
          )}
        </div>

        <div style={{ marginTop: '16px' }}>
          <h4 style={skillHeaderStyle}>Missing Required Skills</h4>
          {matchResult.missing_skills.length > 0 ? (
            <div style={pillContainerStyle}>
              {matchResult.missing_skills.map((s, i) => (
                <span key={i} style={{ ...pillStyle, color: 'var(--color-danger)', borderColor: 'rgba(239, 68, 68, 0.3)', background: 'rgba(239, 68, 68, 0.05)' }}>
                  {s}
                </span>
              ))}
            </div>
          ) : (
            <span style={{ ...emptyTextStyle, color: 'var(--color-success)' }}>All Required Skills Matched!</span>
          )}
        </div>

        {(matchResult.preferred_skills_matched.length > 0 || matchResult.preferred_skills_missing.length > 0) && (
          <div style={dividerStyle}></div>
        )}

        {matchResult.preferred_skills_matched.length > 0 && (
          <div>
            <h4 style={skillHeaderStyle}>Matched Preferred Skills</h4>
            <div style={pillContainerStyle}>
              {matchResult.preferred_skills_matched.map((s, i) => (
                <span key={i} style={{ ...pillStyle, color: 'var(--color-info)', borderColor: 'rgba(59, 130, 246, 0.3)', background: 'rgba(59, 130, 246, 0.05)' }}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {matchResult.preferred_skills_missing.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <h4 style={skillHeaderStyle}>Missing Preferred Skills</h4>
            <div style={pillContainerStyle}>
              {matchResult.preferred_skills_missing.map((s, i) => (
                <span key={i} style={{ ...pillStyle, color: 'var(--text-secondary)', borderColor: 'rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.02)' }}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div style={dividerStyle}></div>

      {/* Reasoning */}
      <div>
        <span style={reasonLabelStyle}>Reasoning Summary</span>
        <p style={reasonTextStyle}>{matchResult.reasoning}</p>
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

const contentLayoutStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-around',
  flexWrap: 'wrap',
  gap: '20px',
};

const gaugeContainerStyle: React.CSSProperties = {
  position: 'relative',
  width: '180px',
  height: '130px',
  display: 'flex',
  justifyContent: 'center',
  overflow: 'hidden',
};

const gaugeLabelStyle: React.CSSProperties = {
  position: 'absolute',
  bottom: '10px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
};

const scoreTextStyle: React.CSSProperties = {
  fontSize: '1.8rem',
  fontWeight: 800,
  fontFamily: 'Outfit, sans-serif',
};

const scoreSubtextStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: 'var(--text-secondary)',
};

const infoStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
  minWidth: '220px',
};

const recContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

const recLabelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const recBadgeStyle: React.CSSProperties = {
  fontSize: '1.1rem',
  fontWeight: 700,
  padding: '6px 16px',
  borderRadius: '8px',
  border: '1px solid',
  textAlign: 'center',
  fontFamily: 'Outfit, sans-serif',
};

const eligibilityBadgeStyle: React.CSSProperties = {
  fontSize: '0.95rem',
  fontWeight: 600,
  padding: '6px 12px',
  borderRadius: '8px',
  textAlign: 'center',
};

const dividerStyle: React.CSSProperties = {
  height: '1px',
  background: 'rgba(255, 255, 255, 0.05)',
  margin: '20px 0',
};

const skillsSectionStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const skillHeaderStyle: React.CSSProperties = {
  fontSize: '0.9rem',
  color: 'var(--text-secondary)',
  marginBottom: '8px',
  fontWeight: 600,
};

const pillContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '8px',
};

const pillStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  fontWeight: 500,
  padding: '3px 10px',
  borderRadius: '6px',
  border: '1px solid',
};

const emptyTextStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-muted)',
  fontStyle: 'italic',
};

const reasonLabelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  display: 'block',
  marginBottom: '6px',
};

const reasonTextStyle: React.CSSProperties = {
  fontSize: '0.9rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.5,
};

const breakdownSectionStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

const breakdownLabelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  display: 'block',
  marginBottom: '6px',
};

const breakdownContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '14px',
  background: 'rgba(255, 255, 255, 0.02)',
  padding: '16px',
  borderRadius: '10px',
  border: '1px solid rgba(255, 255, 255, 0.03)',
};

const breakdownItemStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const breakdownHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  fontWeight: 500,
};

const breakdownValueStyle: React.CSSProperties = {
  fontWeight: 700,
  color: 'var(--text-primary)',
};

const breakdownSubtextStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  fontWeight: 400,
};

const progressTrackStyle: React.CSSProperties = {
  height: '6px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '3px',
  overflow: 'hidden',
  width: '100%',
};

const progressFillStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '3px',
  transition: 'width 0.3s ease-in-out',
};
