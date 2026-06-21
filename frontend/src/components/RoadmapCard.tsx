// Career Roadmap Card Component

import React, { useState } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { CareerRoadmap, MatchResult, SkillGapReport } from '../types';

interface RoadmapCardProps {
  roadmap: CareerRoadmap;
  matchResult: MatchResult;
  gapReport: SkillGapReport;
}

export const RoadmapCard: React.FC<RoadmapCardProps> = ({ roadmap, matchResult, gapReport }) => {
  const [selectedWeek, setSelectedWeek] = useState<number>(1);

  // Compute projection data
  const currentScore = matchResult.match_score;
  const lookup: Record<string, number> = {};
  if (gapReport.recommendations) {
    gapReport.recommendations.forEach(r => {
      lookup[r.skill.toLowerCase().trim()] = r.estimated_improvement_score;
    });
  }

  const projectionData = [
    { name: 'Current', Score: parseFloat(currentScore.toFixed(1)) }
  ];

  let cumulativeScore = currentScore;
  roadmap.roadmap_weeks.forEach(w => {
    let weekGain = 0;
    w.tasks.forEach(t => {
      weekGain += lookup[t.skill.toLowerCase().trim()] || 0;
    });
    cumulativeScore = Math.min(100.0, cumulativeScore + weekGain);
    projectionData.push({
      name: `Week ${w.week_number}`,
      Score: parseFloat(cumulativeScore.toFixed(1))
    });
  });

  const getDifficultyColor = (diff: string) => {
    switch (diff) {
      case 'BEGINNER':
        return '#10b981';
      case 'INTERMEDIATE':
        return '#3b82f6';
      case 'ADVANCED':
        return '#a855f7';
      default:
        return 'var(--text-secondary)';
    }
  };

  const currentActiveWeek = roadmap.roadmap_weeks.find(w => w.week_number === selectedWeek);

  return (
    <div className="glass-card" style={cardStyle}>
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Career Roadmap</h3>

      <div style={flexHeaderStyle}>
        <div>
          <span style={labelStyle}>Duration</span>
          <span style={valStyle}>{roadmap.total_weeks} {roadmap.total_weeks === 1 ? 'Week' : 'Weeks'}</span>
        </div>
        <div>
          <span style={labelStyle}>Expected Match Score Gain</span>
          <span style={{ ...valStyle, color: 'var(--color-success)' }}>
            +{roadmap.expected_match_score_improvement.toFixed(1)}%
          </span>
        </div>
      </div>

      <p style={summaryTextStyle}>{roadmap.roadmap_summary}</p>

      <div style={dividerStyle}></div>

      {/* Projection Chart */}
      <div style={chartWrapperStyle}>
        <h4 style={chartTitleStyle}>Score Improvement Projection</h4>
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={projectionData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
            <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} domain={[0, 100]} />
            <Tooltip 
              contentStyle={{ background: 'rgba(15, 18, 36, 0.95)', borderColor: 'var(--border-neon)' }}
              labelStyle={{ color: 'var(--text-primary)' }}
            />
            <Line type="monotone" dataKey="Score" stroke="#6366f1" strokeWidth={3} activeDot={{ r: 6 }} dot={{ strokeWidth: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={dividerStyle}></div>

      {/* Tab selectors */}
      <div style={tabBarContainerStyle}>
        <span style={tabBarLabelStyle}>Weekly Schedule</span>
        <div style={tabContainerStyle}>
          {roadmap.roadmap_weeks.map(w => (
            <button 
              key={w.week_number} 
              style={{
                ...tabBtnStyle,
                background: selectedWeek === w.week_number ? 'var(--accent-primary)' : 'rgba(255,255,255,0.02)',
                borderColor: selectedWeek === w.week_number ? '#818cf8' : 'var(--border-neon)',
                color: selectedWeek === w.week_number ? '#ffffff' : 'var(--text-secondary)',
              }}
              onClick={() => setSelectedWeek(w.week_number)}
            >
              Week {w.week_number}
            </button>
          ))}
        </div>
      </div>

      {/* Weekly tasks list */}
      <div style={{ marginTop: '16px' }}>
        {currentActiveWeek && currentActiveWeek.tasks.length > 0 ? (
          <div style={taskListStyle}>
            {currentActiveWeek.tasks.map((task, idx) => {
              const diffColor = getDifficultyColor(task.difficulty);
              return (
                <div key={idx} style={taskItemStyle}>
                  <div style={taskItemHeaderStyle}>
                    <div style={taskTitleBoxStyle}>
                      <span style={{ ...diffBadgeStyle, background: `${diffColor}15`, color: diffColor, borderColor: diffColor }}>
                        {task.difficulty}
                      </span>
                      <strong>{task.title}</strong>
                    </div>
                    <span style={hoursBadgeStyle}>
                      ⏳ {task.estimated_hours.toFixed(1)} hrs
                    </span>
                  </div>
                  <p style={taskDescStyle}>{task.description}</p>
                  <span style={skillBadgeStyle}>Skill Focus: {task.skill}</span>
                </div>
              );
            })}
          </div>
        ) : (
          <span style={emptyTextStyle}>No tasks scheduled for this week.</span>
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
  marginBottom: '16px',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  display: 'block',
  marginBottom: '4px',
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

const chartWrapperStyle: React.CSSProperties = {
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

const tabBarContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const tabBarLabelStyle: React.CSSProperties = {
  fontSize: '0.9rem',
  color: 'var(--text-primary)',
  fontWeight: 600,
};

const tabContainerStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
  flexWrap: 'wrap',
};

const tabBtnStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  fontWeight: 600,
  padding: '8px 16px',
  borderRadius: '6px',
  border: '1px solid',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  fontFamily: 'Outfit, sans-serif',
};

const taskListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

const taskItemStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  padding: '16px',
};

const taskItemHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '10px',
  flexWrap: 'wrap',
  gap: '8px',
};

const taskTitleBoxStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  fontSize: '0.95rem',
};

const diffBadgeStyle: React.CSSProperties = {
  fontSize: '0.65rem',
  fontWeight: 700,
  padding: '2px 6px',
  borderRadius: '4px',
  border: '1px solid',
};

const hoursBadgeStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  fontWeight: 600,
  color: 'var(--text-secondary)',
};

const taskDescStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.5,
  marginBottom: '8px',
};

const skillBadgeStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: '#818cf8',
  background: 'rgba(99, 102, 241, 0.1)',
  padding: '2px 8px',
  borderRadius: '4px',
  fontWeight: 500,
};

const emptyTextStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-muted)',
  fontStyle: 'italic',
};
