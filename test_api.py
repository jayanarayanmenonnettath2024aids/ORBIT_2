"""Test analytics API endpoint"""
import requests

# Test analytics endpoint
url = "http://localhost:5000/api/analytics/user_001"
print(f"Testing: {url}")

try:
    response = requests.get(url)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print("\n✅ Response Success!")
        print("\n� Full Response:")
        import json
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")
