import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileBuilder from './ProfileBuilder';
import OpportunityExplorer from './OpportunityExplorer';
import ApplicationTracker from './ApplicationTracker';
import AIChatbot from './AIChatbot';
import AnalyticsDashboard from './AnalyticsDashboard';
import GamificationDisplay from './GamificationDisplay';
import SuccessStories from './SuccessStories';
import { FileText, Search, Sparkles, ClipboardList, RefreshCw, BarChart3, Trophy, LogOut } from 'lucide-react';
import { updateLoginStreak } from '../utils/gamification';
import { logoutUser } from '../services/api';

function Dashboard({ profile, setProfile, opportunities, setOpportunities }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('explore'); // Start with explore if profile exists
  const [showUpdateProfile, setShowUpdateProfile] = useState(false);
  const [showGreeting, setShowGreeting] = useState(true);
  
  // Get user ID and name from localStorage or profile
  const userId = localStorage.getItem('user_id') || profile?.profile_id || 'default-user';
  const userName = localStorage.getItem('user_name') || profile?.personal_info?.name || 'there';

  // Handle logout
  const handleLogout = async () => {
    try {
      await logoutUser();
      // Clear all localStorage
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_email');
      localStorage.removeItem('user_name');
      localStorage.removeItem('userProfile');
      sessionStorage.clear();
      // Navigate to landing page
      navigate('/');
    } catch (err) {
      console.error('Logout error:', err);
      // Still clear localStorage and navigate even if API call fails
      localStorage.clear();
      sessionStorage.clear();
      navigate('/');
    }
  };

  // Show greeting on first load
  useEffect(() => {
    const hasShownGreeting = sessionStorage.getItem('hasShownGreeting');
    if (!hasShownGreeting) {
      sessionStorage.setItem('hasShownGreeting', 'true');
      // Auto-hide greeting after 8 seconds
      setTimeout(() => setShowGreeting(false), 8000);
    } else {
      setShowGreeting(false);
    }
    
    // Update login streak on dashboard load
    updateLoginStreak();
  }, []);

  // Load profile from localStorage on mount
  useEffect(() => {
    const savedProfile = localStorage.getItem('userProfile');
    if (savedProfile && !profile) {
      try {
        const parsedProfile = JSON.parse(savedProfile);
        setProfile(parsedProfile);
        setActiveTab('explore'); // Go straight to explore if profile exists
        console.log('✅ Loaded saved profile from localStorage');
      } catch (err) {
        console.error('Failed to parse saved profile:', err);
        localStorage.removeItem('userProfile');
      }
    } else if (!profile) {
      setActiveTab('profile'); // No profile, start with profile builder
    }
  }, []);

  // Save profile to localStorage whenever it changes
  useEffect(() => {
    if (profile) {
      localStorage.setItem('userProfile', JSON.stringify(profile));
      console.log('✅ Profile saved to localStorage');
    }
  }, [profile]);

  return (
    <div className="dashboard">
      <div className="container">
        {/* Personalized Greeting Banner */}
        {showGreeting && (
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '20px 30px',
            borderRadius: '12px',
            marginBottom: '20px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            animation: 'slideDown 0.5s ease-out'
          }}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>
              👋 Hi {userName}!
            </h3>
            <p style={{ margin: '0 0 12px 0', opacity: 0.95 }}>
              Welcome back! Ready to discover new opportunities?
            </p>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              💡 <strong>Quick tip:</strong> Check your Application Tracker to see how your applications are progressing!
            </p>
          </div>
        )}
        
        {/* Welcome Section */}
        <div className="welcome-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 className="welcome-title">
                <Sparkles className="icon" />
                Welcome to Your Opportunity Journey
              </h2>
              <p className="welcome-text">
                This system doesn't just tell you if you're eligible it shows you the path to become eligible.
              </p>
            </div>            <button 
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
              }}
            >
              <LogOut size={18} />
              Logout
            </button>            {profile && (
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setShowUpdateProfile(true);
                  setActiveTab('profile');
                }}
                style={{ minWidth: '160px' }}
              >
                <RefreshCw className="icon-sm" />
                Update Profile
              </button>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-nav">
          {(!profile || showUpdateProfile) && (
            <button
              className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <FileText className="icon-sm" />
              {profile ? 'Update Your Profile' : 'Step 1: Build Your Profile'}
            </button>
          )}
          <button
            className={`tab-button ${activeTab === 'explore' ? 'active' : ''}`}
            onClick={() => setActiveTab('explore')}
            disabled={!profile}
          >
            <Search className="icon-sm" />
            {profile && !showUpdateProfile ? 'Explore Opportunities' : 'Step 2: Explore Opportunities'}
          </button>
          <button
            className={`tab-button ${activeTab === 'tracker' ? 'active' : ''}`}
            onClick={() => setActiveTab('tracker')}
            disabled={!profile}
          >
            <ClipboardList className="icon-sm" />
            Application Tracker
          </button>
          <button
            className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
            disabled={!profile}
          >
            <BarChart3 className="icon-sm" />
            Analytics & Rankings
          </button>
          <button
            className={`tab-button ${activeTab === 'success' ? 'active' : ''}`}
            onClick={() => setActiveTab('success')}
            disabled={!profile}
          >
            <Trophy className="icon-sm" />
            Success Stories
          </button>
        </div>

        {/* Gamification Bar */}
        {profile && <GamificationDisplay userId={userId} />}

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'profile' && (
            <ProfileBuilder 
              onProfileCreated={(newProfile) => {
                setProfile(newProfile);
                setShowUpdateProfile(false);
                setActiveTab('explore');
              }}
              existingProfile={profile}
            />
          )}

          {activeTab === 'explore' && profile && (
            <OpportunityExplorer 
              profile={profile}
              opportunities={opportunities}
              setOpportunities={setOpportunities}
            />
          )}

          {activeTab === 'tracker' && profile && (
            <ApplicationTracker userId={userId} />
          )}

          {activeTab === 'analytics' && profile && (
            <AnalyticsDashboard userId={userId} />
          )}

          {activeTab === 'success' && profile && (
            <SuccessStories />
          )}
        </div>

        {/* AI Chatbot - Always visible */}
        {profile && (
          <AIChatbot 
            userId={userId}
            context={{ profile: profile }}
          />
        )}

        {/* Info Cards */}
        <div className="info-cards">
          <div className="info-card">
            <h3>🎯 What Makes This Different?</h3>
            <ul>
              <li>Real opportunities from Google Search</li>
              <li>AI-powered eligibility analysis using Gemini</li>
              <li>Clear explanations, not just yes/no</li>
              <li>Actionable guidance to become eligible</li>
            </ul>
          </div>

          <div className="info-card">
            <h3>🚀 How It Works</h3>
            <ol>
              <li>Create your profile (resume or manual)</li>
              <li>Search for opportunities</li>
              <li>Get AI analysis of your eligibility</li>
              <li>Follow personalized guidance to improve</li>
            </ol>
          </div>

          <div className="info-card">
            <h3>💡 Our Philosophy</h3>
            <p>
              We believe eligibility is a journey, not a gate. 
              Every "not yet eligible" comes with a roadmap to get there.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
