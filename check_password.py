"""Check actual password in database"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# Initialize
cred = credentials.Certificate(r'C:\Users\JAYAN\Downloads\orbit\backend\firebase-credentials.json')
try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Get first user
user_doc = db.collection('users').document('user_001').get()
if user_doc.exists:
    user_data = user_doc.to_dict()
    stored_hash = user_data.get('password_hash')
    
    # Try both passwords
    pwd1 = "AaravSharma@100"
    pwd2 = "AaravSharma@101"
    
    hash1 = hashlib.sha256(pwd1.encode()).hexdigest()
    hash2 = hashlib.sha256(pwd2.encode()).hexdigest()
    
    print(f"Email: {user_data.get('email')}")
    print(f"Stored hash: {stored_hash}")
    print(f"\nTesting passwords:")
    print(f"1. {pwd1} -> {hash1}")
    print(f"   Match: {hash1 == stored_hash}")
    print(f"2. {pwd2} -> {hash2}")
    print(f"   Match: {hash2 == stored_hash}")
