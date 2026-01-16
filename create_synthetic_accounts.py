"""
Create Authentication Accounts for Synthetic Users
"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
import hashlib

# Initialize
cred = credentials.Certificate(r'C:\Users\JAYAN\Downloads\orbit\backend\firebase-credentials.json')
try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 60)
print("🔐 Creating Auth Accounts for Synthetic Users")
print("=" * 60)

# Get all synthetic profiles
profiles = db.collection('profiles').where('is_synthetic', '==', True).stream()

created_count = 0
skipped_count = 0
error_count = 0

for profile_doc in profiles:
    user_id = profile_doc.id
    profile_data = profile_doc.to_dict()
    
    email = f"{user_id}@example.com"
    password = "password123"
    
    try:
        # Check if user already exists in users collection
        user_doc = db.collection('users').document(user_id).get()
        
        if user_doc.exists:
            print(f"⏭️  Skipped {user_id} (already exists)")
            skipped_count += 1
            continue
        
        # Create user document in users collection (for local auth)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'user_id': user_id,
            'name': profile_data.get('personal_info', {}).get('name', 'Anonymous'),
            'created_at': datetime.now().isoformat(),
            'is_synthetic': True,
            'auth_provider': 'local'
        }
        
        db.collection('users').document(user_id).set(user_data)
        created_count += 1
        
        if created_count % 20 == 0:
            print(f"  ✓ Created {created_count} accounts...")
        
    except Exception as e:
        print(f"  ⚠️  Error creating {user_id}: {e}")
        error_count += 1

print(f"\n✅ Created {created_count} new accounts")
print(f"⏭️  Skipped {skipped_count} existing accounts")
if error_count > 0:
    print(f"⚠️  {error_count} errors")

print("\n" + "=" * 60)
print("📝 Test Credentials (email / password):")
print("=" * 60)
print("1. synthetic_user_1@example.com / password123")
print("2. synthetic_user_25@example.com / password123")
print("3. synthetic_user_50@example.com / password123")
print("4. synthetic_user_75@example.com / password123")
print("5. synthetic_user_100@example.com / password123")
print("\nAll 100 users: synthetic_user_[1-100]@example.com / password123")
print("=" * 60)
