import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './AnalyticsDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function AnalyticsDashboard({ userId }) {
  const [analytics, setAnalytics] = useState(null);
  const [leaderboardStats, setLeaderboardStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, [userId]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL;

      // Fetch all analytics data
      const [analyticsRes, leaderboardRes, insightsRes] = await Promise.all([
        fetch(`${apiUrl}/analytics/${userId}`),
        fetch(`${apiUrl}/analytics/leaderboard/${userId}`),
        fetch(`${apiUrl}/analytics/insights/${userId}`)
      ]);

      if (analyticsRes.ok) {
        const data = await analyticsRes.json();
        setAnalytics(data);
      }

      if (leaderboardRes.ok) {
        const data = await leaderboardRes.json();
        setLeaderboardStats(data);
      }

      if (insightsRes.ok) {
        const data = await insightsRes.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="analytics-error">No analytics data available</div>;
  }

  const stats = analytics.statistics;
  const peerComparison = analytics.peer_comparison;

  // Prepare data for charts
  const statusData = [
    { name: 'Pending', value: stats.pending },
    { name: 'Under Review', value: stats.under_review },
    { name: 'Accepted', value: stats.accepted },
    { name: 'Rejected', value: stats.rejected }
  ].filter(item => item.value > 0);

  const categoryData = Object.entries(stats.categories).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  const monthlyTrendData = Object.entries(stats.monthly_trend).map(([month, count]) => ({
    month: new Date(month + '-01').toLocaleDateString('default', { month: 'short' }),
    applications: count
  }));

  const comparisonData = peerComparison ? [
    {
      metric: 'Points',
      You: stats.total_points,
      Average: peerComparison.avg_points
    },
    {
      metric: 'Applications',
      You: stats.total_applications,
      Average: peerComparison.avg_applications
    }
  ] : [];

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2>📊 Analytics Dashboard</h2>
        <p className="analytics-subtitle">Track your progress and compare with peers</p>
      </div>

      {/* Insights Section */}
      {insights.length > 0 && (
        <div className="insights-section">
          {insights.map((insight, idx) => (
            <div key={idx} className={`insight-card insight-${insight.type}`}>
              <span className="insight-icon">{insight.icon}</span>
              <p>{insight.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="analytics-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'ranking' ? 'active' : ''}
          onClick={() => setActiveTab('ranking')}
        >
          Rankings
        </button>
        <button
          className={activeTab === 'activity' ? 'active' : ''}
          onClick={() => setActiveTab('activity')}
        >
          Activity
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="analytics-content">
          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📝</div>
              <div className="metric-value">{stats.total_applications}</div>
              <div className="metric-label">Total Applications</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">✅</div>
              <div className="metric-value">{stats.acceptance_rate}%</div>
              <div className="metric-label">Acceptance Rate</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-value">{stats.avg_eligibility_score}%</div>
              <div className="metric-label">Avg Eligibility</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🔥</div>
              <div className="metric-value">{stats.login_streak}</div>
              <div className="metric-label">Day Streak</div>
            </div>
          </div>

          {/* Charts Row 1 */}
          <div className="charts-row">
            {/* Application Status Pie Chart */}
            <div className="chart-card">
              <h3>Application Status</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Monthly Trend Line Chart */}
            <div className="chart-card">
              <h3>Monthly Trend</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={monthlyTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="applications"
                    stroke="#8884d8"
                    strokeWidth={2}
                    dot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Charts Row 2 */}
          <div className="charts-row">
            {/* Category Distribution Bar Chart */}
            {categoryData.length > 0 && (
              <div className="chart-card">
                <h3>Applications by Category</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#0088FE" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Peer Comparison */}
            {peerComparison && (
              <div className="chart-card">
                <h3>You vs Peers</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="You" fill="#00C49F" />
                    <Bar dataKey="Average" fill="#FFBB28" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rankings Tab */}
      {activeTab === 'ranking' && leaderboardStats && (
        <div className="rankings-content">
          <div className="rank-overview">
            <div className="rank-card main-rank">
              <h3>Your Rank</h3>
              <div className="rank-number">#{leaderboardStats.user_rank}</div>
              <p>out of {leaderboardStats.total_users} users</p>
              <div className="percentile">
                Top {(100 - leaderboardStats.percentile).toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="surrounding-users">
            <h3>Leaderboard Position</h3>
            {leaderboardStats.surrounding_users.map((user) => (
              <div
                key={user.rank}
                className={`leaderboard-row ${user.is_current_user ? 'current-user' : ''}`}
              >
                <div className="rank-badge">#{user.rank}</div>
                <div className="user-name">{user.name}</div>
                <div className="user-points">{user.points} pts</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Tab */}
      {activeTab === 'activity' && (
        <div className="activity-content">
          <h3>Recent Activity</h3>
          <div className="activity-timeline">
            {analytics.timeline.map((event, idx) => (
              <div key={idx} className="timeline-item">
                <div className="timeline-icon">{event.icon}</div>
                <div className="timeline-content">
                  <p className="timeline-action">{event.action}</p>
                  <p className="timeline-time">
                    {new Date(event.timestamp).toLocaleDateString()} at{' '}
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsDashboard;
