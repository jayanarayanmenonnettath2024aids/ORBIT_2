"""
Gamification Service - Points, badges, levels, and achievements
"""

from datetime import datetime
import random


class GamificationService:
    def __init__(self, firebase_service):
        """Initialize gamification service"""
        self.firebase = firebase_service
        self.db = firebase_service.db
        
        # Points system
        self.POINT_VALUES = {
            'profile_complete': 100,
            'search_opportunity': 5,
            'check_eligibility': 10,
            'save_to_tracker': 15,
            'apply_submitted': 50,
            'status_update': 10,
            'chat_message': 2,
            'daily_login': 20,
            'streak_bonus': 10,  # Per day of streak
            'resume_upload': 50,
            'profile_update': 15
        }
        
        # Level thresholds
        self.LEVELS = [
            {'level': 1, 'name': 'Beginner', 'min_points': 0, 'icon': '🌱'},
            {'level': 2, 'name': 'Explorer', 'min_points': 100, 'icon': '🔍'},
            {'level': 3, 'name': 'Achiever', 'min_points': 300, 'icon': '⭐'},
            {'level': 4, 'name': 'Expert', 'min_points': 600, 'icon': '🎯'},
            {'level': 5, 'name': 'Master', 'min_points': 1000, 'icon': '👑'},
            {'level': 6, 'name': 'Legend', 'min_points': 2000, 'icon': '🏆'}
        ]
        
        # Achievements/Badges
        self.ACHIEVEMENTS = {
            'first_search': {'name': 'First Steps', 'description': 'Searched your first opportunity', 'icon': '👣', 'points': 10},
            'tracker_starter': {'name': 'Tracker Starter', 'description': 'Saved first opportunity to tracker', 'icon': '📌', 'points': 25},
            'applicant': {'name': 'Applicant', 'description': 'Marked first application as submitted', 'icon': '📝', 'points': 50},
            'consistent': {'name': 'Consistent Explorer', 'description': '7-day login streak', 'icon': '🔥', 'points': 100},
            'super_consistent': {'name': 'Dedicated Hunter', 'description': '30-day login streak', 'icon': '💪', 'points': 300},
            'social': {'name': 'Chatty', 'description': 'Sent 50 chat messages', 'icon': '💬', 'points': 50},
            'organized': {'name': 'Organized Pro', 'description': 'Tracked 10 opportunities', 'icon': '📊', 'points': 100},
            'completionist': {'name': 'Profile Perfect', 'description': 'Completed 100% of profile', 'icon': '✨', 'points': 150},
            'early_bird': {'name': 'Early Bird', 'description': 'Applied within 24h of discovering', 'icon': '🐦', 'points': 75},
            'go_getter': {'name': 'Go-Getter', 'description': 'Applied to 5 opportunities', 'icon': '🚀', 'points': 200}
        }
    
    def get_user_gamification(self, user_id):
        """Get complete gamification profile for user"""
        try:
            # Get or create gamification document
            gami_ref = self.db.collection('gamification').document(user_id)
            gami_doc = gami_ref.get()
            
            if not gami_doc.exists:
                # Initialize new user
                initial_data = {
                    'user_id': user_id,
                    'total_points': 0,
                    'level': 1,
                    'achievements': [],
                    'last_login': datetime.now().isoformat(),
                    'login_streak': 0,
                    'actions': {
                        'searches': 0,
                        'eligibility_checks': 0,
                        'tracker_saves': 0,
                        'applications': 0,
                        'chat_messages': 0
                    },
                    'created_at': datetime.now().isoformat()
                }
                gami_ref.set(initial_data)
                return self._calculate_gamification_status(initial_data)
            
            data = gami_doc.to_dict()
            return self._calculate_gamification_status(data)
            
        except Exception as e:
            print(f"Error getting gamification: {e}")
            return None
    
    def award_points(self, user_id, action, metadata=None):
        """Award points for user action and check for level-ups/achievements"""
        try:
            gami_ref = self.db.collection('gamification').document(user_id)
            gami_doc = gami_ref.get()
            
            if not gami_doc.exists:
                # Initialize if doesn't exist
                self.get_user_gamification(user_id)
                gami_doc = gami_ref.get()
            
            data = gami_doc.to_dict()
            
            # Award points
            points = self.POINT_VALUES.get(action, 0)
            old_points = data['total_points']
            new_points = old_points + points
            
            # Update action counter
            action_map = {
                'search_opportunity': 'searches',
                'check_eligibility': 'eligibility_checks',
                'save_to_tracker': 'tracker_saves',
                'apply_submitted': 'applications',
                'chat_message': 'chat_messages'
            }
            
            if action in action_map:
                counter_key = action_map[action]
                data['actions'][counter_key] = data.get('actions', {}).get(counter_key, 0) + 1
            
            # Check for level up
            old_level = self._get_level_from_points(old_points)
            new_level = self._get_level_from_points(new_points)
            leveled_up = new_level['level'] > old_level['level']
            
            # Check for new achievements
            new_achievements = self._check_achievements(data, action, metadata)
            
            # Update database
            gami_ref.update({
                'total_points': new_points,
                'level': new_level['level'],
                'actions': data['actions'],
                'achievements': data.get('achievements', []) + new_achievements,
                'updated_at': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'points_awarded': points,
                'new_total': new_points,
                'leveled_up': leveled_up,
                'new_level': new_level if leveled_up else None,
                'new_achievements': [self.ACHIEVEMENTS[a] for a in new_achievements]
            }
            
        except Exception as e:
            print(f"Error awarding points: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_login_streak(self, user_id):
        """Update daily login streak"""
        try:
            gami_ref = self.db.collection('gamification').document(user_id)
            gami_doc = gami_ref.get()
            
            if not gami_doc.exists:
                return self.award_points(user_id, 'daily_login')
            
            data = gami_doc.to_dict()
            last_login = datetime.fromisoformat(data.get('last_login', datetime.now().isoformat()))
            now = datetime.now()
            
            # Check if last login was yesterday
            days_diff = (now.date() - last_login.date()).days
            
            if days_diff == 1:
                # Continue streak
                new_streak = data.get('login_streak', 0) + 1
                bonus_points = self.POINT_VALUES['daily_login'] + (new_streak * self.POINT_VALUES['streak_bonus'])
            elif days_diff == 0:
                # Same day, no change
                return {'success': True, 'message': 'Already logged in today'}
            else:
                # Streak broken, restart
                new_streak = 1
                bonus_points = self.POINT_VALUES['daily_login']
            
            gami_ref.update({
                'last_login': now.isoformat(),
                'login_streak': new_streak,
                'total_points': data['total_points'] + bonus_points
            })
            
            return {
                'success': True,
                'streak': new_streak,
                'points_awarded': bonus_points
            }
            
        except Exception as e:
            print(f"Error updating streak: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_leaderboard(self, limit=50):
        """Get top users by points"""
        try:
            users = self.db.collection('gamification')\
                .order_by('total_points', direction='DESCENDING')\
                .limit(limit)\
                .stream()
            
            leaderboard = []
            for rank, doc in enumerate(users, 1):
                data = doc.to_dict()
                user_id = data['user_id']
                
                # Get user profile name
                try:
                    profile = self.db.collection('profiles').document(user_id).get()
                    name = profile.to_dict().get('personal_info', {}).get('name', 'Anonymous User')
                except:
                    name = 'Anonymous User'
                
                level_info = self._get_level_from_points(data['total_points'])
                
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_id,
                    'name': name,
                    'points': data['total_points'],
                    'level': level_info['level'],
                    'level_name': level_info['name'],
                    'level_icon': level_info['icon'],
                    'achievements_count': len(data.get('achievements', [])),
                    'login_streak': data.get('login_streak', 0)
                })
            
            return leaderboard
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def _calculate_gamification_status(self, data):
        """Calculate current level, progress, and achievements"""
        points = data['total_points']
        level_info = self._get_level_from_points(points)
        
        # Calculate progress to next level
        next_level_idx = level_info['level']
        if next_level_idx < len(self.LEVELS):
            next_level = self.LEVELS[next_level_idx]
            progress = ((points - level_info['min_points']) / 
                       (next_level['min_points'] - level_info['min_points'])) * 100
        else:
            next_level = None
            progress = 100
        
        # Get achievement details
        earned_achievements = [
            {**self.ACHIEVEMENTS[a], 'id': a} 
            for a in data.get('achievements', [])
        ]
        
        return {
            'user_id': data['user_id'],
            'total_points': points,
            'level': level_info['level'],
            'level_name': level_info['name'],
            'level_icon': level_info['icon'],
            'progress_to_next': round(progress, 1),
            'next_level': next_level,
            'achievements': earned_achievements,
            'achievements_count': len(earned_achievements),
            'login_streak': data.get('login_streak', 0),
            'actions': data.get('actions', {})
        }
    
    def _get_level_from_points(self, points):
        """Get level information from points"""
        for i in range(len(self.LEVELS) - 1, -1, -1):
            if points >= self.LEVELS[i]['min_points']:
                return self.LEVELS[i]
        return self.LEVELS[0]
    
    def _check_achievements(self, data, action, metadata):
        """Check if action unlocks new achievements"""
        new_achievements = []
        current_achievements = data.get('achievements', [])
        
        # First search
        if action == 'search_opportunity' and data['actions'].get('searches', 0) == 1:
            if 'first_search' not in current_achievements:
                new_achievements.append('first_search')
        
        # First tracker save
        if action == 'save_to_tracker' and data['actions'].get('tracker_saves', 0) == 1:
            if 'tracker_starter' not in current_achievements:
                new_achievements.append('tracker_starter')
        
        # First application
        if action == 'apply_submitted' and data['actions'].get('applications', 0) == 1:
            if 'applicant' not in current_achievements:
                new_achievements.append('applicant')
        
        # 7-day streak
        if data.get('login_streak', 0) >= 7 and 'consistent' not in current_achievements:
            new_achievements.append('consistent')
        
        # 30-day streak
        if data.get('login_streak', 0) >= 30 and 'super_consistent' not in current_achievements:
            new_achievements.append('super_consistent')
        
        # 50 chat messages
        if data['actions'].get('chat_messages', 0) >= 50 and 'social' not in current_achievements:
            new_achievements.append('social')
        
        # 10 tracked opportunities
        if data['actions'].get('tracker_saves', 0) >= 10 and 'organized' not in current_achievements:
            new_achievements.append('organized')
        
        # 5 applications
        if data['actions'].get('applications', 0) >= 5 and 'go_getter' not in current_achievements:
            new_achievements.append('go_getter')
        
        return new_achievements
