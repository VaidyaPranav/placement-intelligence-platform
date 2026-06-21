// Student Profile Card Component

import React from 'react';
import { StudentProfile } from '../types';

interface StudentProfileCardProps {
  profile: StudentProfile;
}

export const StudentProfileCard: React.FC<StudentProfileCardProps> = ({ profile }) => {
  return (
    <div className="glass-card">
      <h3 style={sectionTitleStyle} className="glow-text-indigo">Student Profile</h3>
      
      <div style={metaGridStyle}>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Name</span>
          <span style={valueStyle}>{profile.name}</span>
        </div>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Department</span>
          <span style={valueStyle}>{profile.department}</span>
        </div>
        <div style={metaItemStyle}>
          <span style={labelStyle}>CGPA</span>
          <span style={{ ...valueStyle, color: 'var(--color-info)' }}>{profile.cgpa.toFixed(2)}</span>
        </div>
        <div style={metaItemStyle}>
          <span style={labelStyle}>Target Role Category</span>
          <span style={{ ...valueStyle, color: '#a855f7' }}>{profile.target_role_category}</span>
        </div>
      </div>

      <div style={dividerStyle}></div>

      <div style={blockStyle}>
        <h4 style={subTitleStyle}>Technical Skills</h4>
        <div style={tagContainerStyle}>
          {profile.skills.map((skill, idx) => (
            <span key={idx} style={tagStyle}>
              {skill}
            </span>
          ))}
        </div>
      </div>

      {profile.projects && profile.projects.length > 0 && (
        <div style={blockStyle}>
          <h4 style={subTitleStyle}>Projects</h4>
          <div style={listStyle}>
            {profile.projects.map((project: any, idx: number) => (
              <div key={idx} style={listItemStyle}>
                <div style={itemHeaderStyle}>
                  <strong>{project.title}</strong>
                  {project.complexity_score && (
                    <span style={badgeStyle}>Complexity: {project.complexity_score}/10</span>
                  )}
                </div>
                {project.description && <p style={descriptionStyle}>{project.description}</p>}
                {project.technologies && project.technologies.length > 0 && (
                  <p style={subtextStyle}>Tech: {project.technologies.join(', ')}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {profile.certifications && profile.certifications.length > 0 && (
        <div style={blockStyle}>
          <h4 style={subTitleStyle}>Certifications</h4>
          <div style={tagContainerStyle}>
            {profile.certifications.map((cert: any, idx: number) => (
              <span key={idx} style={{ ...tagStyle, background: 'rgba(59, 130, 246, 0.1)', borderColor: 'rgba(59, 130, 246, 0.2)' }}>
                {typeof cert === 'string' ? cert : cert.name || 'Certification'}
              </span>
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
  gridTemplateColumns: 'repeat(2, 1fr)',
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

const blockStyle: React.CSSProperties = {
  marginBottom: '20px',
};

const subTitleStyle: React.CSSProperties = {
  fontSize: '1rem',
  marginBottom: '10px',
  color: 'var(--text-secondary)',
  fontWeight: 600,
};

const tagContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '8px',
};

const tagStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  background: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.2)',
  borderRadius: '6px',
  padding: '4px 10px',
};

const listStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

const listItemStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  padding: '12px',
};

const itemHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '6px',
  fontSize: '0.95rem',
};

const badgeStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  background: 'rgba(168, 85, 247, 0.15)',
  color: '#c084fc',
  padding: '2px 8px',
  borderRadius: '10px',
  fontWeight: 500,
};

const descriptionStyle: React.CSSProperties = {
  fontSize: '0.85rem',
  color: 'var(--text-secondary)',
  lineHeight: 1.4,
  marginBottom: '4px',
};

const subtextStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-muted)',
};
