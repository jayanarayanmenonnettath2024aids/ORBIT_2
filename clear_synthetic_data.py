"""
Clear Synthetic Data from Firebase
"""

import os
import sys

os.chdir(r'C:\Users\JAYAN\Downloads\orbit\backend')
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

# Prevent Flask app from starting
import builtins
original_input = builtins.input

from services.firebase_service import FirebaseService


def clear_synthetic_data():
    """Remove all synthetic data from Firebase"""
    print("=" * 60)
    print("🗑️  ORBIT - Clear Synthetic Data")
    print("=" * 60)
    
    confirm = original_input("\n⚠️  This will delete all synthetic users and applications. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    print("\n🔧 Initializing Firebase...")
    firebase = FirebaseService()
    db = firebase.db
    print("✅ Firebase connected!")
    
    # Clear gamification
    print("\n🗑️  Clearing synthetic gamification data...")
    gami_docs = db.collection('gamification').where('is_synthetic', '==', True).stream()
    count = 0
    for doc in gami_docs:
        doc.reference.delete()
        count += 1
        if count % 20 == 0:
            print(f"  ✓ Deleted {count} gamification records...")
    print(f"✅ Deleted {count} gamification records")
    
    # Clear profiles
    print("\n🗑️  Clearing synthetic profiles...")
    profile_docs = db.collection('profiles').where('is_synthetic', '==', True).stream()
    count = 0
    for doc in profile_docs:
        doc.reference.delete()
        count += 1
        if count % 20 == 0:
            print(f"  ✓ Deleted {count} profiles...")
    print(f"✅ Deleted {count} profiles")
    
    # Clear applications
    print("\n🗑️  Clearing synthetic applications...")
    app_docs = db.collection('applications').where('is_synthetic', '==', True).stream()
    count = 0
    for doc in app_docs:
        doc.reference.delete()
        count += 1
        if count % 100 == 0:
            print(f"  ✓ Deleted {count} applications...")
    print(f"✅ Deleted {count} applications")
    
    print("\n" + "=" * 60)
    print("✨ Synthetic data cleared successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        clear_synthetic_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
