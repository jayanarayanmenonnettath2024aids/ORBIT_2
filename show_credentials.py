"""Show sample login credentials"""
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

print("=" * 70)
print("Sample Login Credentials (First 10 users)")
print("=" * 70)

users = db.collection('users').where('is_synthetic', '==', True).limit(10).stream()

for idx, user_doc in enumerate(users, 1):
    user_data = user_doc.to_dict()
    print(f"\n{idx}. {user_data.get('name')}")
    print(f"   Email: {user_data.get('email')}")
    # Extract password from pattern: FirstnameLastname@XXX
    parts = user_data.get('name').split()
    if len(parts) >= 2:
        first, last = parts[0], parts[1]
        # user_001 is index 0, user_002 is index 1, etc.
        user_num = int(user_doc.id.split('_')[1])
        index = user_num - 1  # Convert to 0-based
        password = f"{first}{last}@{100 + index}"
        print(f"   Password: {password}")

print("\n" + "=" * 70)
print("Pattern: Email = firstname.lastname.X@gmail.com")
print("         Password = FirstnameLastname@(100+index)")
print("         Example: user_001 -> aarav.sharma.1@gmail.com / AaravSharma@100")
print("=" * 70)
