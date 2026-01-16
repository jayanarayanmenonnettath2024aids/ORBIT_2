import React from 'react';
import './EligibilityScore.css';

function EligibilityScore({ score, breakdown, recommendation, missingRequirements }) {
  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  const getMaxPoints = (category) => {
    const maxPoints = {
      'education_match': 25,
      'skills_match': 25,
      'experience_match': 20,
      'deadline_feasibility': 15,
      'location_match': 10,
      'other_criteria': 5
    };
    return maxPoints[category] || 25;
  };

  const formatCategoryName = (category) => {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="eligibility-score-widget">
      <div className="score-header">
        <h2>Eligibility Analysis</h2>
      </div>

      <div className="score-main">
        <div className="score-circle" style={{ borderColor: getScoreColor(score) }}>
          <h1 style={{ color: getScoreColor(score) }}>{score}</h1>
          <p>/ 100</p>
        </div>

        <div className="recommendation-box" style={{ borderLeftColor: getScoreColor(score) }}>
          <p className="recommendation-label">Recommendation</p>
          <p className="recommendation-text">{recommendation || 'Calculating...'}</p>
        </div>
      </div>
      
      <div className="score-breakdown">
        <h3>Score Breakdown</h3>
        {breakdown && Object.entries(breakdown).map(([key, value]) => {
          const maxPoints = getMaxPoints(key);
          const percentage = (value / maxPoints) * 100;
          
          return (
            <div key={key} className="breakdown-item">
              <div className="breakdown-header">
                <span className="breakdown-label">{formatCategoryName(key)}</span>
                <span className="breakdown-value">{value}/{maxPoints} pts</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${percentage}%`,
                    backgroundColor: getScoreColor(value * 4)
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {missingRequirements && missingRequirements.length > 0 && (
        <div className="missing-requirements">
          <h3>⚠️ Missing Requirements</h3>
          {missingRequirements.map((gap, index) => (
            <div key={index} className="gap-item">
              <p className="gap-category">{gap.category}:</p>
              <ul className="gap-list">
                {gap.missing.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EligibilityScore;
