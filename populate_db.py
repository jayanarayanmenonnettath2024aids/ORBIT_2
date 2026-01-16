"""
Populate Firebase with Synthetic Data - Standalone Script
"""

import os
import sys

# Set working directory
os.chdir(r'C:\Users\JAYAN\Downloads\orbit\backend')
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

# Prevent Flask app from starting
os.environ['WERKZEUG_RUN_MAIN'] = 'false'

from services.firebase_service import FirebaseService
from services.synthetic_data_service import SyntheticDataService
from datetime import datetime
import random


def populate_data():
    """Populate synthetic data into Firebase"""
    print("=" * 60)
    print("🚀 ORBIT - Synthetic Data Population")
    print("=" * 60)
    
    # Initialize Firebase
    print("\n🔧 Initializing Firebase...")
    firebase = FirebaseService()
    db = firebase.db
    print("✅ Firebase connected!")
    
    # Generate users
    print(f"\n🔄 Generating 100 synthetic users (Tier 2/3 colleges)...")
    users = SyntheticDataService.generate_peer_users(100)
    print(f"✅ Generated {len(users)} users")
    
    # Add to database
    print(f"\n📝 Adding to Firebase...")
    added_users = 0
    added_profiles = 0
    
    for user in users:
        user_id = user['user_id']
        
        try:
            # Add gamification data
            gami_ref = db.collection('gamification').document(user_id)
            gami_data = {
                'user_id': user_id,
                'total_points': user['total_points'],
                'level': user['level'],
                'login_streak': user['login_streak'],
                'achievements': user.get('achievements', []),
                'actions': user['actions'],
                'last_login': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'is_synthetic': True,
                'daily_tasks': {},
                'weekly_tasks': {},
                'tasks_completed': 0,
                'last_task_reset': datetime.now().isoformat()
            }
            gami_ref.set(gami_data)
            added_users += 1
            
            # Add profile
            profile_ref = db.collection('profiles').document(user_id)
            profile_data = {
                'user_id': user_id,
                'personal_info': {
                    'name': user['name'],
                    'email': f"{user_id}@example.com"
                },
                'education': {
                    'degree': user['degree'],
                    'major': user['major'],
                    'institution': user['college'],
                    'year': random.choice(['2024', '2025', '2026', '2027'])
                },
                'is_synthetic': True,
                'created_at': datetime.now().isoformat()
            }
            profile_ref.set(profile_data)
            added_profiles += 1
            
            if added_users % 20 == 0:
                print(f"  ✓ Added {added_users} users...")
                
        except Exception as e:
            print(f"  ⚠️  Error adding {user_id}: {e}")
    
    print(f"\n✅ Added {added_users} gamification records")
    print(f"✅ Added {added_profiles} profile records")
    
    # Generate and add applications
    print(f"\n🔄 Generating synthetic applications...")
    applications = SyntheticDataService.generate_peer_applications(100, 8)
    print(f"✅ Generated {len(applications)} applications")
    
    print(f"\n📝 Adding applications to Firebase...")
    added_apps = 0
    
    for i, app in enumerate(applications):
        try:
            app_id = f"synthetic_app_{i+1}"
            app_ref = db.collection('applications').document(app_id)
            
            app_data = {
                'user_id': app['user_id'],
                'opportunity_id': f"opp_{random.randint(1, 100)}",
                'opportunity_title': app['opportunity_title'],
                'category': app['category'],
                'status': app['status'],
                'eligibility_score': app['eligibility_score'],
                'created_at': app['created_at'],
                'updated_at': app['created_at'],
                'is_synthetic': True
            }
            
            app_ref.set(app_data)
            added_apps += 1
            
            if added_apps % 100 == 0:
                print(f"  ✓ Added {added_apps} applications...")
                
        except Exception as e:
            print(f"  ⚠️  Error adding app {i+1}: {e}")
    
    print(f"\n✅ Added {added_apps} applications")
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Synthetic Data Population Complete!")
    print("=" * 60)
    print(f"📊 Total Users: {added_users}")
    print(f"📊 Total Profiles: {added_profiles}")
    print(f"📊 Total Applications: {added_apps}")
    print(f"🎓 Colleges: Tier 2/3 (LPU, Amity, SRM, AKTU, etc.)")
    print(f"🔥 Active Leaderboard: 100+ users for competition!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        populate_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
