// Interview Card Component

import React, { useState } from 'react';
import { InterviewPreparationReport } from '../types';

interface InterviewCardProps {
  interviewReport: InterviewPreparationReport;
}

export const InterviewCard: React.FC<InterviewCardProps> = ({ interviewReport }) => {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const toggleQuestion = (idx: number) => {
    if (expandedIdx === idx) {
      setExpandedIdx(null);
    } else {
      setExpandedIdx(idx);
    }
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff) {
      case 'EASY':
        return '#10b981';
      case 'MEDIUM':
        return '#f59e0b';
      case 'HARD':
        return '#ef4444';
      default:
        return 'var(--text-secondary)';
    }
  };

  return (
    <div className="glass-card" style={cardStyle}>
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Interview Preparation Pack</h3>

      <div style={flexHeaderStyle}>
        <div>
          <span style={labelStyle}>Readiness Score</span>
          <span style={valStyle}>{interviewReport.estimated_interview_readiness_score}/100</span>
        </div>
        <div>
          <span style={labelStyle}>Overall Difficulty</span>
          <span style={{ 
            ...valStyle, 
            color: getDifficultyColor(interviewReport.overall_difficulty)
          }}>
            {interviewReport.overall_difficulty}
          </span>
        </div>
      </div>

      <p style={summaryTextStyle}>{interviewReport.preparation_summary}</p>

      <div style={dividerStyle}></div>

      {/* Focus Areas */}
      <div style={focusSectionStyle}>
        <span style={labelStyle}>Key Focus Areas</span>
        <div style={tagContainerStyle}>
          {interviewReport.focus_areas && interviewReport.focus_areas.length > 0 ? (
            interviewReport.focus_areas.map((area, idx) => (
              <span key={idx} style={focusTagStyle}>
                🎯 {area}
              </span>
            ))
          ) : (
            <span style={emptyTextStyle}>No specific focus areas identified. Ready for mock rounds!</span>
          )}
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Technical Questions */}
      <div style={blockStyle}>
        <h4 style={subHeaderStyle}>Technical & Coding Questions</h4>
        <p style={tipTextStyle}>Click a question to view expected keywords and evaluation rubrics.</p>
        
        <div style={accordionContainerStyle}>
          {interviewReport.technical_questions.map((q, idx) => {
            const isExpanded = expandedIdx === idx;
            const diffColor = getDifficultyColor(q.difficulty);
            return (
              <div key={idx} style={accordionItemStyle}>
                <div 
                  style={{
                    ...accordionHeaderStyle,
                    background: isExpanded ? 'rgba(255, 255, 255, 0.04)' : 'rgba(255, 255, 255, 0.01)',
                  }}
                  onClick={() => toggleQuestion(idx)}
                >
                  <div style={headerTextContainerStyle}>
                    <span style={{ ...diffBadgeStyle, background: `${diffColor}15`, color: diffColor, borderColor: diffColor }}>
                      {q.difficulty}
                    </span>
                    <span style={skillBadgeStyle}>{q.skill}</span>
                    <strong style={questionTextStyle}>{q.question}</strong>
                  </div>
                  <span style={arrowStyle}>{isExpanded ? '▲' : '▼'}</span>
                </div>

                {isExpanded && (
                  <div style={accordionBodyStyle}>
                    <div style={bodyBlockStyle}>
                      <span style={bodyLabelStyle}>Expected Answer Keywords</span>
                      <div style={keywordContainerStyle}>
                        {q.expected_answer_keywords.map((kw, i) => (
                          <span key={i} style={keywordTagStyle}>{kw}</span>
                        ))}
                      </div>
                    </div>

                    <div style={bodyBlockStyle}>
                      <span style={bodyLabelStyle}>Objective Evaluation Rubric</span>
                      <ol style={rubricListStyle}>
                        {q.evaluation_rubric.map((item, i) => (
                          <li key={i} style={rubricItemStyle}>{item}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div style={dividerStyle}></div>

      {/* Behavioral Questions */}
      <div>
        <h4 style={subHeaderStyle}>Behavioral & Scenario Questions</h4>
        <div style={behavioralGridStyle}>
          {interviewReport.behavioral_questions.map((q, idx) => (
            <div key={idx} style={behavioralCardStyle}>
              <div style={bCardHeaderStyle}>
                <span style={bCardNumStyle}>Q{idx+1}</span>
                <span style={bCardBadgeStyle}>Behavioral</span>
              </div>
              <p style={bQuestionTextStyle}>{q.question}</p>
            </div>
          ))}
        </div>
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
  marginBottom: '16px',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  display: 'block',
  marginBottom: '6px',
};

const valStyle: React.CSSProperties = {
  fontSize: '1.4rem',
  fontWeight: 700,
  fontFamily: 'Outfit, sans-serif',
};

const summaryTextStyle: React.CSSProperties = {
  fontSize: '0.95rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.5,
};

const dividerStyle: React.CSSProperties = {
  height: '1px',
  background: 'rgba(255, 255, 255, 0.05)',
  margin: '20px 0',
};

const focusSectionStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const tagContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '8px',
};

const focusTagStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  fontWeight: 600,
  background: 'rgba(245, 158, 11, 0.1)',
  border: '1px solid rgba(245, 158, 11, 0.2)',
  borderRadius: '8px',
  padding: '6px 12px',
  color: '#fbbf24',
};

const emptyTextStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-muted)',
  fontStyle: 'italic',
};

const blockStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const subHeaderStyle: React.CSSProperties = {
  fontSize: '1.1rem',
  color: 'var(--text-primary)',
  marginBottom: '8px',
  fontWeight: 600,
};

const tipTextStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-muted)',
  marginBottom: '16px',
};

const accordionContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const accordionItemStyle: React.CSSProperties = {
  border: '1px solid var(--border-neon)',
  borderRadius: '8px',
  overflow: 'hidden',
  background: 'rgba(255, 255, 255, 0.01)',
};

const accordionHeaderStyle: React.CSSProperties = {
  padding: '16px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  cursor: 'pointer',
  userSelect: 'none',
  transition: 'background 0.2s ease',
};

const headerTextContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  flexWrap: 'wrap',
};

const diffBadgeStyle: React.CSSProperties = {
  fontSize: '0.65rem',
  fontWeight: 700,
  padding: '2px 6px',
  borderRadius: '4px',
  border: '1px solid',
};

const skillBadgeStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  fontWeight: 600,
  color: 'var(--color-info)',
  background: 'rgba(59, 130, 246, 0.1)',
  padding: '2px 8px',
  borderRadius: '4px',
};

const questionTextStyle: React.CSSProperties = {
  fontSize: '0.95rem',
  lineHeight: 1.4,
};

const arrowStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
};

const accordionBodyStyle: React.CSSProperties = {
  padding: '16px',
  background: 'rgba(0, 0, 0, 0.2)',
  borderTop: '1px solid rgba(255, 255, 255, 0.03)',
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const bodyBlockStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const bodyLabelStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  fontWeight: 600,
};

const keywordContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '6px',
};

const keywordTagStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '2px 8px',
  borderRadius: '4px',
  border: '1px solid rgba(255,255,255,0.05)',
  color: 'var(--text-primary)',
};

const rubricListStyle: React.CSSProperties = {
  paddingLeft: '18px',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

const rubricItemStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
};

const behavioralGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
  gap: '12px',
};

const behavioralCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  padding: '14px',
};

const bCardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '8px',
};

const bCardNumStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  fontWeight: 800,
  color: '#c084fc',
};

const bCardBadgeStyle: React.CSSProperties = {
  fontSize: '0.65rem',
  fontWeight: 600,
  background: 'rgba(168, 85, 247, 0.1)',
  color: '#c084fc',
  padding: '2px 6px',
  borderRadius: '4px',
};

const bQuestionTextStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.45,
};
