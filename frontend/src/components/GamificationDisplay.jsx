import { useState, useEffect } from 'react';
import './GamificationDisplay.css';

function GamificationDisplay({ userId }) {
  const [gamification, setGamification] = useState(null);
  const [showAchievements, setShowAchievements] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    fetchGamification();
  }, [userId]);

  const fetchGamification = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const response = await fetch(`${apiUrl}/gamification/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setGamification(data);
      }
    } catch (error) {
      console.error('Error fetching gamification:', error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const response = await fetch(`${apiUrl}/gamification/leaderboard?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data);
        setShowLeaderboard(true);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  if (!gamification) {
    return null;
  }

  return (
    <>
      {/* Compact Gamification Bar */}
      <div className="gamification-bar">
        <div className="gami-level" title={`Level ${gamification.level}: ${gamification.level_name}`}>
          <span className="level-icon">{gamification.level_icon}</span>
          <span className="level-text">Lv.{gamification.level}</span>
        </div>

        <div className="gami-points" title="Total Points">
          <span className="points-icon">⭐</span>
          <span className="points-text">{gamification.total_points}</span>
        </div>

        <div className="gami-progress" title={`${gamification.progress_to_next}% to next level`}>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${gamification.progress_to_next}%` }}
            />
          </div>
          {gamification.next_level && (
            <span className="next-level">{gamification.next_level.name}</span>
          )}
        </div>

        <div className="gami-streak" title={`${gamification.login_streak} day streak`}>
          <span className="streak-icon">🔥</span>
          <span className="streak-text">{gamification.login_streak}</span>
        </div>

        <button className="gami-achievements-btn" onClick={() => setShowAchievements(true)}>
          <span>🏆</span>
          <span>{gamification.achievements_count}</span>
        </button>

        <button className="gami-leaderboard-btn" onClick={fetchLeaderboard}>
          <span>📊</span>
          <span>Ranks</span>
        </button>
      </div>

      {/* Achievements Modal */}
      {showAchievements && (
        <div className="modal-overlay" onClick={() => setShowAchievements(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🏆 Achievements</h2>
              <button className="modal-close" onClick={() => setShowAchievements(false)}>×</button>
            </div>
            <div className="achievements-grid">
              {gamification.achievements.map((achievement) => (
                <div key={achievement.id} className="achievement-card earned">
                  <div className="achievement-icon">{achievement.icon}</div>
                  <div className="achievement-name">{achievement.name}</div>
                  <div className="achievement-desc">{achievement.description}</div>
                  <div className="achievement-points">+{achievement.points} pts</div>
                </div>
              ))}
              {gamification.achievements.length === 0 && (
                <p className="no-achievements">No achievements yet. Keep exploring opportunities!</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Modal */}
      {showLeaderboard && (
        <div className="modal-overlay" onClick={() => setShowLeaderboard(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📊 Global Leaderboard</h2>
              <button className="modal-close" onClick={() => setShowLeaderboard(false)}>×</button>
            </div>
            <div className="leaderboard-list">
              {leaderboard.map((user, idx) => (
                <div
                  key={user.user_id}
                  className={`leaderboard-item ${user.user_id === userId ? 'current-user' : ''} ${idx < 3 ? 'top-3' : ''}`}
                >
                  <div className="lb-rank">
                    {idx === 0 && '🥇'}
                    {idx === 1 && '🥈'}
                    {idx === 2 && '🥉'}
                    {idx > 2 && `#${user.rank}`}
                  </div>
                  <div className="lb-info">
                    <div className="lb-name">{user.name}</div>
                    <div className="lb-level">
                      {user.level_icon} {user.level_name} • {user.achievements_count} achievements
                    </div>
                  </div>
                  <div className="lb-points">{user.points} pts</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default GamificationDisplay;
