import React, { useState } from 'react';
import { Search, ExternalLink, ChevronDown, ChevronUp, CheckCircle, AlertCircle, Clock, Bookmark } from 'lucide-react';
import { searchOpportunities, analyzeEligibility } from '../services/api';

function OpportunityExplorer({ profile, opportunities, setOpportunities }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [analyzing, setAnalyzing] = useState({});
  const [analyses, setAnalyses] = useState({});
  const [expandedOpp, setExpandedOpp] = useState(null);
  const [saving, setSaving] = useState({});

  const handleSaveToTracker = async (opportunity) => {
    const oppId = opportunity.opportunity_id;
    setSaving(prev => ({ ...prev, [oppId]: true }));
    
    try {
      // Get userId from multiple sources
      const userId = localStorage.getItem('userId') || 
                     profile?.profile_id || 
                     profile?.user_id;
      
      if (!userId) {
        alert('❌ Please log in to save opportunities');
        setSaving(prev => ({ ...prev, [oppId]: false }));
        return;
      }
      
      const analysis = analyses[oppId];
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      
      console.log('API URL:', apiUrl);
      console.log('Saving to tracker:', {
        user_id: userId,
        opportunity_title: opportunity.title,
        opportunity_link: opportunity.link
      });
      
      // Test backend connectivity first
      try {
        const healthCheck = await fetch(`${apiUrl}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        });
        if (!healthCheck.ok) {
          throw new Error('Backend server is not responding');
        }
      } catch (healthErr) {
        console.error('Backend health check failed:', healthErr);
        alert('❌ Cannot connect to backend server. Please ensure:\n1. Backend is running (python app.py in backend folder)\n2. Server is on http://localhost:5000\n3. No firewall blocking the connection');
        setSaving(prev => ({ ...prev, [oppId]: false }));
        return;
      }
      
      const response = await fetch(`${apiUrl}/applications`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          opportunity_title: opportunity.title,
          opportunity_link: opportunity.link,
          deadline: opportunity.deadline || 'Not specified',
          eligibility_score: analysis?.confidence_score || null,
          priority: 'medium',
          notes: ''
        }),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });
      
      const data = await response.json();
      
      if (response.ok) {
        console.log('✅ Saved successfully:', data);
        alert('✅ Saved to Application Tracker! Check the tracker tab.');
      } else {
        console.error('❌ Save failed:', data);
        throw new Error(data.error || `Server error: ${response.status}`);
      }
    } catch (err) {
      console.error('Save error:', err);
      if (err.name === 'TimeoutError') {
        alert('❌ Request timeout. Backend server may be slow or not running.');
      } else if (err.message.includes('fetch')) {
        alert('❌ Network error: Cannot connect to backend.\nPlease check:\n• Backend server is running\n• No firewall blocking localhost:5000');
      } else {
        alert(`❌ Failed to save: ${err.message}`);
      }
    } finally {
      setSaving(prev => ({ ...prev, [oppId]: false }));
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const result = await searchOpportunities(searchQuery);
      setOpportunities(result.opportunities);
    } catch (err) {
      console.error('Search failed:', err);
      alert('Failed to search opportunities');
    } finally {
      setSearching(false);
    }
  };

  const handleAnalyze = async (opportunityId) => {
    setAnalyzing(prev => ({ ...prev, [opportunityId]: true }));
    
    try {
      const result = await analyzeEligibility(profile.profile_id, opportunityId);
      setAnalyses(prev => ({
        ...prev,
        [opportunityId]: result
      }));
    } catch (err) {
      console.error('Analysis failed:', err);
      console.error('Error details:', err.response?.data);
      const errorMessage = err.response?.data?.error || 'Failed to analyze eligibility';
      alert(errorMessage);
    } finally {
      setAnalyzing(prev => ({ ...prev, [opportunityId]: false }));
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'Eligible': { icon: CheckCircle, color: 'green', text: 'Eligible' },
      'Partially Eligible': { icon: Clock, color: 'yellow', text: 'Partially Eligible' },
      'Not Yet Eligible': { icon: AlertCircle, color: 'red', text: 'Not Yet Eligible' }
    };

    const badge = badges[status] || badges['Partially Eligible'];
    const Icon = badge.icon;

    return (
      <div className={`status-badge status-${badge.color}`}>
        <Icon className="icon-sm" />
        {badge.text}
      </div>
    );
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 50) return 'yellow';
    return 'red';
  };

  return (
    <div className="opportunity-explorer">
      <h2>Discover Opportunities</h2>
      <p className="subtitle">Search for real opportunities from across the web</p>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search for hackathons, internships, fellowships..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            disabled={searching}
          />
          <button type="submit" disabled={searching} className="btn btn-primary">
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Quick Search Suggestions */}
      <div className="quick-searches">
        <span className="label">Quick searches:</span>
        {['AI hackathon', 'software internship', 'student fellowship', 'coding competition'].map(term => (
          <button
            key={term}
            className="quick-search-btn"
            onClick={() => {
              setSearchQuery(term);
              searchOpportunities(term).then(result => setOpportunities(result.opportunities));
            }}
          >
            {term}
          </button>
        ))}
      </div>

      {/* Results */}
      {opportunities.length > 0 && (
        <div className="opportunities-list">
          <h3>{opportunities.length} Opportunities Found</h3>

          {opportunities.map((opp) => {
            const analysis = analyses[opp.opportunity_id];
            const isExpanded = expandedOpp === opp.opportunity_id;
            const isAnalyzing = analyzing[opp.opportunity_id];

            return (
              <div key={opp.opportunity_id} className="opportunity-card">
                <div className="opp-header">
                  <div className="opp-main-info">
                    <h4>{opp.title}</h4>
                    <p className="opp-organizer">{opp.organizer}</p>
                    <div className="opp-meta">
                      <span className="opp-type">{opp.type}</span>
                      {opp.deadline && (
                        <span className="opp-deadline">Deadline: {opp.deadline}</span>
                      )}
                    </div>
                  </div>
                  <div className="opp-actions">
                    {analysis ? (
                      <div className="analysis-summary">
                        {getStatusBadge(analysis.eligibility_status)}
                        <div className="confidence-score">
                          <span className={`confidence-value confidence-${getConfidenceColor(analysis.confidence_score)}`}>
                            {analysis.confidence_score}%
                          </span>
                          <span className="confidence-label">confidence</span>
                        </div>
                      </div>
                    ) : (
                      <button
                        className="btn btn-primary"
                        onClick={() => handleAnalyze(opp.opportunity_id)}
                        disabled={isAnalyzing}
                      >
                        {isAnalyzing ? 'Analyzing...' : 'Check Eligibility'}
                      </button>
                    )}
                  </div>
                </div>

                <p className="opp-snippet">{opp.snippet}</p>

                <div className="opp-footer">
                  <a 
                    href={opp.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-text"
                  >
                    <ExternalLink className="icon-sm" />
                    View Details
                  </a>

                  <button
                    className="btn btn-secondary"
                    onClick={() => handleSaveToTracker(opp)}
                    disabled={saving[opp.opportunity_id]}
                  >
                    <Bookmark className="icon-sm" />
                    {saving[opp.opportunity_id] ? 'Saving...' : 'Save to Tracker'}
                  </button>

                  {analysis && (
                    <button
                      className="btn btn-text"
                      onClick={() => setExpandedOpp(isExpanded ? null : opp.opportunity_id)}
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="icon-sm" />
                          Hide Analysis
                        </>
                      ) : (
                        <>
                          <ChevronDown className="icon-sm" />
                          Show Detailed Analysis
                        </>
                      )}
                    </button>
                  )}
                </div>

                {/* Expanded Analysis - PREMIUM DETAILED UI */}
                {analysis && isExpanded && (
                  <div className="analysis-details-premium">
                    {/* Header with Status Badge */}
                    <div className="analysis-header-premium">
                      <div className="analysis-badge-container">
                        {getStatusBadge(analysis.eligibility_status)}
                        <div className={`confidence-pill confidence-${getConfidenceColor(analysis.confidence_score)}`}>
                          <span className="confidence-label">Match Score</span>
                          <span className="confidence-value">{analysis.confidence_score}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Hero Section with Summary */}
                    <div className="analysis-hero">
                      <div className="analysis-summary-card">
                        <div className="summary-icon">📊</div>
                        <div className="analysis-summary-content">
                          <h4>Analysis Summary</h4>
                          <p className="summary-text">{analysis.explanation_simple}</p>
                        </div>
                      </div>
                    </div>

                    {/* Analysis Grid - Strengths vs Gaps */}
                    <div className="analysis-grid">
                      {/* What You Have */}
                      {analysis.reasons_met && analysis.reasons_met.length > 0 && (
                        <div className="analysis-card analysis-card-success">
                          <div className="card-header">
                            <CheckCircle className="card-icon" />
                            <h5>What You Have</h5>
                          </div>
                          <ul className="reasons-list">
                            {analysis.reasons_met.map((reason, idx) => (
                              <li key={idx}>
                                <span className="bullet">✓</span>
                                {reason}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* What's Missing */}
                      {analysis.reasons_not_met && analysis.reasons_not_met.length > 0 && (
                        <div className="analysis-card analysis-card-warning">
                          <div className="card-header">
                            <AlertCircle className="card-icon" />
                            <h5>What's Missing</h5>
                          </div>
                          <ul className="reasons-list">
                            {analysis.reasons_not_met.map((reason, idx) => (
                              <li key={idx}>
                                <span className="bullet">!</span>
                                {reason}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Skills to Develop */}
                    {analysis.missing_skills && analysis.missing_skills.length > 0 && (
                      <div className="analysis-section-premium">
                        <div className="section-header">
                          <div className="section-icon">🎯</div>
                          <h5>Skills to Develop</h5>
                        </div>
                        <div className="skill-tags-premium">
                          {analysis.missing_skills.map((skill, idx) => (
                            <span key={idx} className="skill-chip">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Next Steps Timeline - PREMIUM FEATURE */}
                    {analysis.next_steps && analysis.next_steps.length > 0 && (
                      <div className="next-steps-premium">
                        <div className="section-header-large">
                          <div className="section-icon-large">🚀</div>
                          <div>
                            <h4>Your Path Forward</h4>
                            <p className="section-subtitle">
                              Follow these steps to become eligible
                            </p>
                          </div>
                        </div>
                        <div className="steps-timeline">
                          {analysis.next_steps.map((step, idx) => (
                            <div key={idx} className="next-step-card">
                              <div className="step-number">{idx + 1}</div>
                              <div className="step-content">
                                <h6>{step.action}</h6>
                                <p className="step-reason">{step.reason}</p>
                                <span className="step-time">
                                  <Clock className="icon-xs" />
                                  {step.time_estimate}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {opportunities.length === 0 && !searching && (
        <div className="empty-state">
          <Search className="icon-lg" />
          <h3>No opportunities yet</h3>
          <p>Search for opportunities to get started</p>
        </div>
      )}
    </div>
  );
}

export default OpportunityExplorer;
