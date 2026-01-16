"""Test analytics for user_001"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase directly
cred = credentials.Certificate(r'C:\Users\JAYAN\Downloads\orbit\backend\firebase-credentials.json')
try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(cred)

db = firestore.client()

db = firestore.client()

# Test user_001
user_id = 'user_001'
print("="*70)
print(f"Testing Data for {user_id}")
print("="*70)

# Get gamification data
gami = db.collection('gamification').document(user_id).get().to_dict()
apps = list(db.collection('applications').where('user_id', '==', user_id).stream())

print("\n🏆 GAMIFICATION:")
print(f"  Points: {gami.get('total_points', 0)}")
print(f"  Level: {gami.get('level', 1)}")
print(f"  Streak: {gami.get('login_streak', 0)}")
print(f"  Achievements: {len(gami.get('achievements', []))}")

print(f"\n📝 APPLICATIONS: {len(apps)}")
for i, app in enumerate(apps[:5], 1):
    app_data = app.to_dict()
    print(f"  {i}. {app_data.get('opportunity_title')} - {app_data.get('status')}")

print("\n" + "="*70)
