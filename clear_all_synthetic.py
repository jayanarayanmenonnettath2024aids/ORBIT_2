"""Quick Clear Synthetic Data - Standalone"""
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

print("🗑️  Clearing ALL synthetic data...")

# Clear gamification
gami_docs = db.collection('gamification').where('is_synthetic', '==', True).stream()
count = 0
for doc in gami_docs:
    doc.reference.delete()
    count += 1
print(f"✅ Deleted {count} gamification records")

# Clear profiles
profile_docs = db.collection('profiles').where('is_synthetic', '==', True).stream()
count = 0
for doc in profile_docs:
    doc.reference.delete()
    count += 1
print(f"✅ Deleted {count} profiles")

# Clear applications
app_docs = db.collection('applications').where('is_synthetic', '==', True).stream()
count = 0
for doc in app_docs:
    doc.reference.delete()
    count += 1
print(f"✅ Deleted {count} applications")

# Clear users (auth accounts)
user_docs = db.collection('users').where('is_synthetic', '==', True).stream()
count = 0
for doc in user_docs:
    doc.reference.delete()
    count += 1
print(f"✅ Deleted {count} user accounts")

print("\n✅ All synthetic data cleared!")
