import React, { useState, useEffect } from 'react';
import './ApplicationTracker.css';
import { trackStatusUpdate } from '../utils/gamification';

function ApplicationTracker({ userId }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    applied: 0,
    under_review: 0,
    accepted: 0
  });

  useEffect(() => {
    fetchApplications();
  }, [userId]);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      console.log('📋 ApplicationTracker - Fetching for userId:', userId);
      console.log('📋 localStorage user_id:', localStorage.getItem('user_id'));
      const apiUrl = import.meta.env.VITE_API_URL;
      console.log('API URL:', apiUrl);
      
      const response = await fetch(`${apiUrl}/applications/${userId}`);
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received applications:', data);
      
      // Ensure data is an array
      const appsArray = Array.isArray(data) ? data : [];
      setApplications(appsArray);
      calculateStats(appsArray);
    } catch (error) {
      console.error('Error fetching applications:', error);
      alert('Failed to load applications. Check console for details.');
      setApplications([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (apps) => {
    setStats({
      total: apps.length,
      applied: apps.filter(a => a.status === 'applied').length,
      under_review: apps.filter(a => a.status === 'under_review').length,
      accepted: apps.filter(a => a.status === 'accepted').length
    });
  };

  const updateStatus = async (appId, newStatus) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/applications/${appId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchApplications();
      
      // Track status update for gamification
      trackStatusUpdate(appId, newStatus);
    } catch (error) {
      console.error('Error updating application:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      saved: '#6b7280',
      applied: '#3b82f6',
      under_review: '#f59e0b',
      accepted: '#10b981',
      rejected: '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  return (
    <div className="application-tracker">
      <h2>📊 Application Tracker</h2>
      
      {/* Stats Dashboard */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.total}</h3>
          <p>Total Tracked</p>
        </div>
        <div className="stat-card">
          <h3>{stats.applied}</h3>
          <p>Applied</p>
        </div>
        <div className="stat-card">
          <h3>{stats.under_review}</h3>
          <p>Under Review</p>
        </div>
        <div className="stat-card">
          <h3>{stats.accepted}</h3>
          <p>Accepted</p>
        </div>
      </div>

      {/* Applications List */}
      {loading ? (
        <p>Loading applications...</p>
      ) : (
        <div className="applications-list">
          {applications.length === 0 ? (
            <p className="empty-state">No applications tracked yet. Start by searching for opportunities!</p>
          ) : (
            applications.map(app => (
              <div key={app.id} className="application-card">
                <div className="app-header">
                  <h3>{app.opportunity_title}</h3>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(app.status) }}
                  >
                    {app.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                
                {app.deadline && (
                  <p className="app-deadline">⏰ Deadline: {app.deadline}</p>
                )}
                
                {app.eligibility_score && (
                  <p className="app-score">📈 Eligibility Score: {app.eligibility_score}%</p>
                )}
                
                {app.notes && (
                  <p className="app-notes">📝 {app.notes}</p>
                )}
                
                <div className="app-actions">
                  <select 
                    value={app.status} 
                    onChange={(e) => updateStatus(app.id, e.target.value)}
                    className="status-select"
                  >
                    <option value="saved">Saved</option>
                    <option value="applied">Applied</option>
                    <option value="under_review">Under Review</option>
                    <option value="accepted">Accepted</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  
                  <a 
                    href={app.opportunity_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-link"
                  >
                    View Opportunity →
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default ApplicationTracker;
