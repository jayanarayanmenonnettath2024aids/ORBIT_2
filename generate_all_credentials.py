"""Generate complete credentials list for all 100 users"""
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

print("Fetching all 100 synthetic users...")
users = db.collection('users').where('is_synthetic', '==', True).limit(100).stream()

credentials_list = []
for user_doc in users:
    user_data = user_doc.to_dict()
    parts = user_data.get('name', '').split()
    if len(parts) >= 2:
        first, last = parts[0], parts[1]
        # Extract index from user_id: user_001 is index 0
        user_num = int(user_doc.id.split('_')[1])
        index = user_num - 1
        password = f"{first}{last}@{100 + index}"
        
        credentials_list.append({
            'user_id': user_doc.id,
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'password': password
        })

print(f"\n✅ Found {len(credentials_list)} users\n")
print("="*100)
print(f"{'#':<5} {'Name':<25} {'Email':<40} {'Password':<20}")
print("="*100)

for i, cred in enumerate(credentials_list, 1):
    print(f"{i:<5} {cred['name']:<25} {cred['email']:<40} {cred['password']:<20}")

print("="*100)
print(f"\nTotal: {len(credentials_list)} synthetic user accounts")
print("\nLogin Instructions:")
print("1. Go to http://localhost:5173")
print("2. Use any email/password combination from above")
print("3. Each account has unique stats (points, streak, achievements)")
print("4. Example: aarav.sharma.1@gmail.com / AaravSharma@100")

# Save to file
with open('all_credentials.txt', 'w', encoding='utf-8') as f:
    f.write("="*100 + "\n")
    f.write("ORBIT - 100 Synthetic User Credentials\n")
    f.write("="*100 + "\n\n")
    f.write(f"{'#':<5} {'Name':<25} {'Email':<40} {'Password':<20}\n")
    f.write("-"*100 + "\n")
    for i, cred in enumerate(credentials_list, 1):
        f.write(f"{i:<5} {cred['name']:<25} {cred['email']:<40} {cred['password']:<20}\n")
    f.write("\n" + "="*100 + "\n")
    f.write(f"Total: {len(credentials_list)} accounts\n")
    f.write("\nPattern:\n")
    f.write("  Email: firstname.lastname.X@gmail.com (where X is 1-100)\n")
    f.write("  Password: FirstnameLastname@Y (where Y is 100-199)\n")

print("\n✅ Credentials saved to 'all_credentials.txt'")
