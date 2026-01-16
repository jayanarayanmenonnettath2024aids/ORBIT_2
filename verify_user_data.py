"""Verify user_001 has proper data"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize
cred = credentials.Certificate(r'C:\Users\JAYAN\Downloads\orbit\backend\firebase-credentials.json')
try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Check user_001 data
user_id = 'user_001'

print("="*70)
print(f"Checking data for {user_id}")
print("="*70)

# 1. Check users collection
user_doc = db.collection('users').document(user_id).get()
if user_doc.exists:
    print("\n✅ AUTH ACCOUNT EXISTS")
    print(f"   Email: {user_doc.to_dict().get('email')}")
    print(f"   Name: {user_doc.to_dict().get('name')}")
else:
    print("\n❌ NO AUTH ACCOUNT")

# 2. Check profiles collection
profile_doc = db.collection('profiles').document(user_id).get()
if profile_doc.exists:
    print("\n✅ PROFILE EXISTS")
    profile = profile_doc.to_dict()
    print(f"   College: {profile.get('college')}")
    print(f"   Degree: {profile.get('degree')}")
else:
    print("\n❌ NO PROFILE")

# 3. Check gamification collection
gami_doc = db.collection('gamification').document(user_id).get()
if gami_doc.exists:
    print("\n✅ GAMIFICATION EXISTS")
    gami = gami_doc.to_dict()
    print(f"   Points: {gami.get('points')}")
    print(f"   Login Streak: {gami.get('login_streak')}")
    print(f"   Achievements: {len(gami.get('achievements', []))}")
    print(f"   Level: {gami.get('level')}")
else:
    print("\n❌ NO GAMIFICATION DATA")

# 4. Check applications collection
apps = db.collection('applications').where('user_id', '==', user_id).stream()
app_list = list(apps)
print(f"\n✅ APPLICATIONS: {len(app_list)} found")
if app_list:
    for i, app in enumerate(app_list[:3], 1):
        app_data = app.to_dict()
        print(f"   {i}. {app_data.get('opportunity_title')} - {app_data.get('status')}")

print("\n" + "="*70)
