import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AIStatus } from '../types';

export const GeminiStatusBadge: React.FC = () => {
  const [statusInfo, setStatusInfo] = useState<AIStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await api.getAIStatus();
        setStatusInfo(res);
      } catch (err) {
        console.error('Failed to fetch AI Status:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, []);

  if (loading) {
    return <span style={loadingStyle}>Checking AI...</span>;
  }

  if (!statusInfo) {
    return null;
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'AI_ACTIVE':
        return { text: '🟢 AI ACTIVE', color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' };
      case 'FALLBACK_MODE':
        return { text: '🟡 FALLBACK MODE', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' };
      case 'API_KEY_MISSING':
      default:
        return { text: '🔴 API KEY MISSING', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
    }
  };

  const config = getStatusConfig(statusInfo.status);

  return (
    <div style={{ ...badgeStyle, color: config.color, background: config.bg, borderColor: config.color }}>
      {config.text}
    </div>
  );
};

const badgeStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  fontWeight: 700,
  padding: '6px 14px',
  borderRadius: '20px',
  border: '1px solid',
  fontFamily: 'Outfit, sans-serif',
  display: 'inline-flex',
  alignItems: 'center',
  letterSpacing: '0.03em',
};

const loadingStyle: React.CSSProperties = {
  fontSize: '0.8rem',
  color: 'var(--text-secondary)',
  fontStyle: 'italic',
};
