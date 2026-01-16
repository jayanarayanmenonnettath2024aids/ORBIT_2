import firebase_admin
from firebase_admin import credentials, firestore
import sys
sys.path.append('./backend')

# Initialize Firebase
cred = credentials.Certificate('./backend/firebase-credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Get applications for user_001
apps = db.collection('applications').where(filter=firestore.FieldFilter('user_id', '==', 'user_001')).stream()

print("Applications for user_001:")
for app in apps:
    data = app.to_dict()
    print(f"\nID: {app.id}")
    print(f"  Title: {data.get('title', 'N/A')}")
    print(f"  Status: {data.get('status', 'N/A')}")
    print(f"  Created at: {data.get('created_at', 'N/A')} (type: {type(data.get('created_at'))})")
