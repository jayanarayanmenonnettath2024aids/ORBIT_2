"""
Analytics Service - User statistics, peer comparison, and insights
"""

from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    def __init__(self, firebase_service):
        """Initialize analytics service"""
        self.firebase = firebase_service
        self.db = firebase_service.db
    
    def get_user_analytics(self, user_id):
        """Get comprehensive analytics for user"""
        try:
            # Get user's applications
            apps = self.db.collection('applications')\
                .where('user_id', '==', user_id)\
                .stream()
            
            applications = [doc.to_dict() for doc in apps]
            
            # Get gamification data
            gami_doc = self.db.collection('gamification').document(user_id).get()
            gami_data = gami_doc.to_dict() if gami_doc.exists else {}
            
            # Calculate statistics
            stats = self._calculate_statistics(applications, gami_data)
            
            # Get activity timeline
            timeline = self._get_activity_timeline(user_id, applications)
            
            # Get peer comparison
            peer_stats = self._get_peer_comparison(user_id, stats)
            
            return {
                'user_id': user_id,
                'statistics': stats,
                'timeline': timeline,
                'peer_comparison': peer_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return None
    
    def get_leaderboard_stats(self, user_id):
        """Get user's rank and surrounding users"""
        try:
            # Get all users sorted by points
            all_users = self.db.collection('gamification')\
                .order_by('total_points', direction='DESCENDING')\
                .stream()
            
            user_rank = None
            total_users = 0
            user_points = 0
            
            for rank, doc in enumerate(all_users, 1):
                total_users = rank
                if doc.id == user_id:
                    user_rank = rank
                    user_points = doc.to_dict()['total_points']
            
            if not user_rank:
                return None
            
            # Get surrounding users (3 above, 3 below)
            surrounding = self.db.collection('gamification')\
                .order_by('total_points', direction='DESCENDING')\
                .limit(user_rank + 3)\
                .stream()
            
            users_list = []
            for rank, doc in enumerate(surrounding, 1):
                if abs(rank - user_rank) <= 3:
                    data = doc.to_dict()
                    # Get profile name
                    try:
                        profile = self.db.collection('profiles').document(doc.id).get()
                        name = profile.to_dict().get('personal_info', {}).get('name', 'Anonymous')
                    except:
                        name = 'Anonymous'
                    
                    users_list.append({
                        'rank': rank,
                        'user_id': doc.id,
                        'name': name,
                        'points': data['total_points'],
                        'is_current_user': doc.id == user_id
                    })
            
            percentile = ((total_users - user_rank) / total_users) * 100 if total_users > 0 else 0
            
            return {
                'user_rank': user_rank,
                'total_users': total_users,
                'percentile': round(percentile, 1),
                'surrounding_users': users_list
            }
            
        except Exception as e:
            print(f"Error getting leaderboard stats: {e}")
            return None
    
    def get_insights(self, user_id):
        """Generate personalized insights and recommendations"""
        try:
            analytics = self.get_user_analytics(user_id)
            if not analytics:
                return []
            
            insights = []
            stats = analytics['statistics']
            
            # Application success rate
            if stats['total_applications'] > 0:
                success_rate = (stats['accepted'] / stats['total_applications']) * 100
                if success_rate > 50:
                    insights.append({
                        'type': 'success',
                        'icon': '🎉',
                        'message': f"Great job! {success_rate:.0f}% acceptance rate!",
                        'priority': 'high'
                    })
                elif success_rate < 20 and stats['total_applications'] > 5:
                    insights.append({
                        'type': 'warning',
                        'icon': '💡',
                        'message': "Consider refining your applications or targeting better-fit opportunities",
                        'priority': 'medium'
                    })
            
            # Activity level
            if stats.get('searches_7d', 0) < 3:
                insights.append({
                    'type': 'tip',
                    'icon': '🔍',
                    'message': "Search more opportunities to increase your chances!",
                    'priority': 'low'
                })
            
            # Application timing
            avg_response = stats.get('avg_response_time', 0)
            if avg_response > 14:
                insights.append({
                    'type': 'tip',
                    'icon': '⏰',
                    'message': "Apply faster! Average response time is over 2 weeks",
                    'priority': 'medium'
                })
            
            # Streak motivation
            streak = stats.get('login_streak', 0)
            if streak >= 7:
                insights.append({
                    'type': 'achievement',
                    'icon': '🔥',
                    'message': f"Amazing! {streak} day streak! Keep it up!",
                    'priority': 'high'
                })
            elif streak == 0:
                insights.append({
                    'type': 'tip',
                    'icon': '📅',
                    'message': "Visit daily to build your streak and earn bonus points!",
                    'priority': 'low'
                })
            
            # Peer comparison
            peer_stats = analytics['peer_comparison']
            if peer_stats:
                if peer_stats['points_percentile'] > 75:
                    insights.append({
                        'type': 'success',
                        'icon': '🏆',
                        'message': f"You're in the top {100 - peer_stats['points_percentile']:.0f}% of users!",
                        'priority': 'high'
                    })
            
            return insights
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return []
    
    def _calculate_statistics(self, applications, gami_data):
        """Calculate user statistics from applications and gamification data"""
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        stats = {
            'total_applications': len(applications),
            'pending': 0,
            'under_review': 0,
            'accepted': 0,
            'rejected': 0,
            'applications_7d': 0,
            'applications_30d': 0,
            'avg_eligibility_score': 0,
            'categories': defaultdict(int),
            'monthly_trend': defaultdict(int)
        }
        
        total_score = 0
        
        for app in applications:
            status = app.get('status', 'pending').lower()
            stats[status] = stats.get(status, 0) + 1
            
            # Eligibility score
            score = app.get('eligibility_score', 0)
            if score:
                total_score += score
            
            # Time-based counts
            created = datetime.fromisoformat(app.get('created_at', now.isoformat()))
            if created >= seven_days_ago:
                stats['applications_7d'] += 1
            if created >= thirty_days_ago:
                stats['applications_30d'] += 1
            
            # Category tracking
            category = app.get('category', 'other')
            stats['categories'][category] += 1
            
            # Monthly trend
            month_key = created.strftime('%Y-%m')
            stats['monthly_trend'][month_key] += 1
        
        # Calculate averages
        if stats['total_applications'] > 0:
            stats['avg_eligibility_score'] = round(total_score / stats['total_applications'], 1)
            stats['acceptance_rate'] = round((stats['accepted'] / stats['total_applications']) * 100, 1)
        else:
            stats['acceptance_rate'] = 0
        
        # Add gamification stats
        stats['total_points'] = gami_data.get('total_points', 0)
        stats['level'] = gami_data.get('level', 1)
        stats['login_streak'] = gami_data.get('login_streak', 0)
        stats['achievements_count'] = len(gami_data.get('achievements', []))
        stats['searches'] = gami_data.get('actions', {}).get('searches', 0)
        stats['eligibility_checks'] = gami_data.get('actions', {}).get('eligibility_checks', 0)
        
        # Convert defaultdicts to regular dicts for JSON
        stats['categories'] = dict(stats['categories'])
        stats['monthly_trend'] = dict(stats['monthly_trend'])
        
        return stats
    
    def _get_activity_timeline(self, user_id, applications):
        """Generate activity timeline"""
        timeline = []
        
        # Add application events
        for app in applications:
            timeline.append({
                'type': 'application',
                'action': f"Applied to {app.get('opportunity_title', 'Unknown')}",
                'timestamp': app.get('created_at'),
                'icon': '📝',
                'status': app.get('status', 'pending')
            })
            
            # Add status updates
            updated = app.get('updated_at')
            if updated and updated != app.get('created_at'):
                timeline.append({
                    'type': 'status_update',
                    'action': f"Status updated: {app.get('status', 'Unknown')}",
                    'timestamp': updated,
                    'icon': '🔄',
                    'status': app.get('status', 'pending')
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Return last 20 events
        return timeline[:20]
    
    def _get_peer_comparison(self, user_id, user_stats):
        """Compare user statistics with peers"""
        try:
            # Get all users' gamification data
            all_users = list(self.db.collection('gamification').stream())
            
            if len(all_users) < 2:
                return None
            
            # Calculate averages
            total_points = [doc.to_dict()['total_points'] for doc in all_users]
            avg_points = sum(total_points) / len(total_points)
            
            # Calculate percentiles
            user_points = user_stats['total_points']
            users_below = sum(1 for p in total_points if p < user_points)
            points_percentile = (users_below / len(total_points)) * 100
            
            # Get peer averages
            peer_apps = []
            for doc in all_users:
                if doc.id != user_id:
                    user_apps = self.db.collection('applications')\
                        .where('user_id', '==', doc.id)\
                        .stream()
                    peer_apps.extend([a.to_dict() for a in user_apps])
            
            avg_peer_apps = len(peer_apps) / (len(all_users) - 1) if len(all_users) > 1 else 0
            
            return {
                'total_users': len(all_users),
                'avg_points': round(avg_points, 0),
                'your_points': user_points,
                'points_percentile': round(points_percentile, 1),
                'avg_applications': round(avg_peer_apps, 1),
                'your_applications': user_stats['total_applications'],
                'performance_vs_peers': 'above' if user_points > avg_points else 'below'
            }
            
        except Exception as e:
            print(f"Error calculating peer comparison: {e}")
            return None
