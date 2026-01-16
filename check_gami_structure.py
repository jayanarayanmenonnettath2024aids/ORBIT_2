"""Check actual gamification structure"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialize
cred = credentials.Certificate(r'C:\Users\JAYAN\Downloads\orbit\backend\firebase-credentials.json')
try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Get full gamification document
gami_doc = db.collection('gamification').document('user_001').get()
if gami_doc.exists:
    gami_data = gami_doc.to_dict()
    print("Full Gamification Data for user_001:")
    print(json.dumps(gami_data, indent=2, default=str))
else:
    print("No gamification data found")

# Check a few more users
print("\n" + "="*70)
print("Checking other synthetic users:")
print("="*70)

for user_num in [1, 2, 3, 50, 100]:
    user_id = f"user_{user_num:03d}"
    gami = db.collection('gamification').document(user_id).get()
    if gami.exists:
        data = gami.to_dict()
        print(f"\n{user_id}:")
        print(f"  Points: {data.get('points')}")
        print(f"  Streak: {data.get('login_streak')}")
        print(f"  Level: {data.get('level')}")
        print(f"  Achievements: {len(data.get('achievements', []))}")
