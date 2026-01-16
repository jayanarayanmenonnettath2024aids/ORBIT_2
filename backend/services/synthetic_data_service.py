"""
Synthetic Data Service - Generate Indian-style peer data for analytics
"""

import random
from datetime import datetime, timedelta


class SyntheticDataService:
    """Generate realistic synthetic Indian student data for peer comparison"""
    
    INDIAN_NAMES = [
        "Aarav Sharma", "Vivaan Patel", "Aditya Kumar", "Arjun Singh", "Sai Reddy",
        "Ananya Gupta", "Diya Verma", "Isha Joshi", "Priya Nair", "Riya Deshmukh",
        "Rohan Mehta", "Karan Malhotra", "Sahil Agarwal", "Yash Rao", "Raj Kapoor",
        "Sneha Iyer", "Neha Sharma", "Kavya Menon", "Tanvi Shah", "Aditi Kulkarni",
        "Arnav Pandey", "Vihaan Chopra", "Ayush Tiwari", "Dev Srinivasan", "Shaurya Bhatt",
        "Anushka Pillai", "Pooja Bose", "Sakshi Dutta", "Meera Chawla", "Divya Saxena",
        "Ishaan Jain", "Reyansh Kumar", "Aadhya Singh", "Vaishnavi Reddy", "Siddharth Nair",
        "Kiara Gupta", "Atharva Desai", "Myra Kapoor", "Kabir Sharma", "Saanvi Patel",
        "Dhruv Mehta", "Navya Iyer", "Advait Shah", "Aanya Verma", "Shaurya Malhotra",
        "Aaradhya Singh", "Vedant Kumar", "Anvi Pillai", "Rudra Agarwal", "Diya Menon"
    ]
    
    # Realistic Tier 2/Tier 3 colleges for the target audience
    COLLEGES = [
        # Tier 2 - Good Private Universities
        "Lovely Professional University", "Amity University", "SRM Institute", 
        "VIT Vellore", "Manipal Institute", "Kalinga Institute",
        "Chitkara University", "Shiv Nadar University", "Bennett University",
        "Chandigarh University", "Thapar Institute", "Symbiosis Institute",
        
        # Tier 3 - State/Regional Colleges
        "Jaipur Engineering College", "Poornima College", "Arya College",
        "Galgotias University", "GL Bajaj Institute", "JECRC University",
        "Sharda University", "Techno India", "Mody University",
        "NIET Greater Noida", "IMS Ghaziabad", "ABES Engineering College",
        "JSS Academy", "PES University", "RV College",
        "Dayananda Sagar College", "BMS College", "MS Ramaiah Institute",
        
        # Government Tier 2/3
        "AKTU Affiliated College", "PTU Affiliated College", "RTU Affiliated College",
        "Gujarat Technological University", "Dr. APJ Abdul Kalam Technical University",
        "Rajasthan Technical University", "Punjab Technical University",
        
        # Regional Universities
        "Savitribai Phule Pune University", "Mumbai University Affiliated",
        "Delhi University Affiliated", "Bangalore University Affiliated",
        "Osmania University", "Andhra University", "Calicut University",
        "Kerala University", "Madras University Affiliated", "Anna University Affiliated"
    ]
    
    DEGREES = ["B.Tech", "B.E.", "BCA", "B.Sc", "M.Tech", "MCA", "MBA"]
    
    MAJORS = [
        "Computer Science", "Information Technology", "Electronics",
        "Mechanical Engineering", "Data Science", "AI & ML", 
        "Software Engineering", "Cybersecurity"
    ]
    
    CATEGORIES = [
        "hackathon", "competition", "internship", "workshop",
        "scholarship", "conference", "research", "project"
    ]
    
    @staticmethod
    def generate_peer_users(count=100):
        """Generate synthetic peer users with realistic Indian data"""
        users = []
        
        for i in range(count):
            user_id = f"synthetic_user_{i+1}"
            
            # Random points (realistic distribution)
            # Most users: 50-500 points
            # Some active: 500-1500
            # Few top performers: 1500-3000
            rand = random.random()
            if rand < 0.6:  # 60% low activity
                points = random.randint(50, 500)
            elif rand < 0.9:  # 30% moderate
                points = random.randint(500, 1500)
            else:  # 10% high performers
                points = random.randint(1500, 3000)
            
            # Level based on points
            if points < 100:
                level = 1
            elif points < 300:
                level = 2
            elif points < 600:
                level = 3
            elif points < 1000:
                level = 4
            elif points < 2000:
                level = 5
            else:
                level = 6
            
            # Realistic activity patterns
            searches = max(1, int(points / 5) + random.randint(-10, 20))
            eligibility_checks = max(0, int(searches * 0.6) + random.randint(-5, 10))
            tracker_saves = max(0, int(eligibility_checks * 0.4) + random.randint(-3, 5))
            applications = max(0, int(tracker_saves * 0.3) + random.randint(-2, 3))
            
            # Streak (most users don't have long streaks)
            streak_rand = random.random()
            if streak_rand < 0.7:  # 70% have 0-3 days
                streak = random.randint(0, 3)
            elif streak_rand < 0.9:  # 20% have 4-10 days
                streak = random.randint(4, 10)
            else:  # 10% have 11+ days
                streak = random.randint(11, 45)
            
            # Achievements (based on activity level)
            achievement_count = min(10, int(points / 300) + random.randint(0, 3))
            
            # Generate realistic achievements based on activity
            achievements = []
            possible_achievements = [
                'first_search', 'first_application', 'tracker_starter', 'applicant',
                'consistent', 'early_bird', 'organized', 'social',
                'completionist', 'go_getter', 'perfectionist', 'task_master',
                'winner', 'champion', 'influencer', 'ultra_consistent', 'scholar'
            ]
            
            # Add achievements based on count
            for j in range(min(achievement_count, len(possible_achievements))):
                achievements.append({
                    'id': possible_achievements[j],
                    'earned_at': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
                })
            
            user = {
                'user_id': user_id,
                'name': random.choice(SyntheticDataService.INDIAN_NAMES),
                'college': random.choice(SyntheticDataService.COLLEGES),
                'degree': random.choice(SyntheticDataService.DEGREES),
                'major': random.choice(SyntheticDataService.MAJORS),
                'total_points': points,
                'level': level,
                'login_streak': streak,
                'actions': {
                    'searches': searches,
                    'eligibility_checks': eligibility_checks,
                    'tracker_saves': tracker_saves,
                    'applications': applications,
                    'chat_messages': random.randint(5, 200)
                },
                'achievements': achievements,
                'is_synthetic': True
            }
            
            users.append(user)
        
        return users
    
    @staticmethod
    def generate_peer_applications(user_count=100, avg_apps_per_user=8):
        """Generate synthetic application data for peer comparison"""
        applications = []
        
        for i in range(user_count):
            user_id = f"synthetic_user_{i+1}"
            
            # Random number of applications per user (realistic distribution)
            num_apps = max(0, int(random.gauss(avg_apps_per_user, 4)))
            
            for j in range(num_apps):
                # Status distribution (realistic)
                status_rand = random.random()
                if status_rand < 0.4:  # 40% pending
                    status = 'pending'
                elif status_rand < 0.6:  # 20% under review
                    status = 'under_review'
                elif status_rand < 0.75:  # 15% accepted
                    status = 'accepted'
                else:  # 25% rejected
                    status = 'rejected'
                
                # Eligibility score (realistic distribution)
                # Most: 60-85
                # Some: 40-60 or 85-95
                score_rand = random.random()
                if score_rand < 0.7:
                    eligibility_score = random.randint(60, 85)
                elif score_rand < 0.85:
                    eligibility_score = random.randint(40, 60)
                else:
                    eligibility_score = random.randint(85, 95)
                
                # Random date in last 6 months
                days_ago = random.randint(1, 180)
                created_at = datetime.now() - timedelta(days=days_ago)
                
                app = {
                    'user_id': user_id,
                    'opportunity_title': f"Opportunity {random.randint(1, 100)}",
                    'category': random.choice(SyntheticDataService.CATEGORIES),
                    'status': status,
                    'eligibility_score': eligibility_score,
                    'created_at': created_at.isoformat(),
                    'is_synthetic': True
                }
                
                applications.append(app)
        
        return applications
    
    @staticmethod
    def calculate_synthetic_peer_stats(user_stats):
        """Calculate peer comparison with synthetic data"""
        synthetic_users = SyntheticDataService.generate_peer_users(100)
        
        # Add real user to pool
        total_users = synthetic_users + [user_stats]
        total_users.sort(key=lambda x: x['total_points'], reverse=True)
        
        # Find user rank
        user_rank = next((i+1 for i, u in enumerate(total_users) 
                         if u.get('user_id') == user_stats.get('user_id')), None)
        
        # Calculate averages from synthetic users only
        avg_points = sum(u['total_points'] for u in synthetic_users) / len(synthetic_users)
        avg_applications = sum(u['actions']['applications'] for u in synthetic_users) / len(synthetic_users)
        avg_streak = sum(u['login_streak'] for u in synthetic_users) / len(synthetic_users)
        
        # Calculate percentile
        users_below = sum(1 for u in total_users if u['total_points'] < user_stats['total_points'])
        percentile = (users_below / len(total_users)) * 100
        
        return {
            'total_users': len(total_users),
            'user_rank': user_rank,
            'percentile': round(percentile, 1),
            'avg_points': round(avg_points, 0),
            'your_points': user_stats['total_points'],
            'avg_applications': round(avg_applications, 1),
            'your_applications': user_stats.get('total_applications', 0),
            'avg_streak': round(avg_streak, 1),
            'your_streak': user_stats.get('login_streak', 0),
            'performance_vs_peers': 'above_average' if user_stats['total_points'] > avg_points else 'below_average',
            'top_users': [
                {
                    'rank': i+1,
                    'name': u['name'],
                    'college': u.get('college', 'Unknown'),
                    'points': u['total_points'],
                    'level': u['level'],
                    'is_you': u.get('user_id') == user_stats.get('user_id')
                }
                for i, u in enumerate(total_users[:10])
            ]
        }
