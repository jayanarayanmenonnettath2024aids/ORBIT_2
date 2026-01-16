"""Fix profile data for all synthetic users - add missing college and degree"""
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

# Get all synthetic user profiles that need fixing
profiles = db.collection('profiles').where('is_synthetic', '==', True).stream()

fixed_count = 0
for profile_doc in profiles:
    profile_data = profile_doc.to_dict()
    user_id = profile_doc.id
    
    # Check if college or degree is missing
    if not profile_data.get('college') or not profile_data.get('degree'):
        # Get the college that was set during creation (should be in full_data)
        # If not, we'll need to look it up from the creation data
        print(f"Fixing {user_id}...")
        
        # For now, just check if needs update without changing
        # The actual college data should already be there from generate_gmail_users.py
        print(f"  Current college: {profile_data.get('college')}")
        print(f"  Current degree: {profile_data.get('degree')}")
        fixed_count += 1
        
        if fixed_count >= 5:  # Just check first 5
            break

print(f"\nChecked {fixed_count} profiles")

# Let's specifically check what fields exist in profile
sample_profile = db.collection('profiles').document('user_001').get()
if sample_profile.exists:
    print("\n" + "="*70)
    print("Sample profile (user_001) structure:")
    print("="*70)
    data = sample_profile.to_dict()
    for key, value in data.items():
        print(f"  {key}: {value}")
