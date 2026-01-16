"""Test if success_stories_service can be imported"""
import sys
sys.path.insert(0, r'C:\Users\JAYAN\Downloads\orbit\backend')

try:
    from services.success_stories_service import SuccessStoriesService
    print("✅ SuccessStoriesService imported successfully!")
    
    # Try to initialize it
    from services.firebase_service import FirebaseService
    firebase = FirebaseService()
    service = SuccessStoriesService(firebase)
    print("✅ SuccessStoriesService initialized!")
    
    # Try to call a method
    stories = service._get_synthetic_success_stories(3)
    print(f"✅ Got {len(stories)} synthetic stories")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
