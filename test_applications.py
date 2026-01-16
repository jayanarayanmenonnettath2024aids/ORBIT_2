import requests

# Test applications endpoint
print("Testing applications endpoint...")
response = requests.get("http://localhost:5000/api/applications/user_001")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Test success stories endpoint
print("\n\nTesting success stories endpoint...")
response = requests.get("http://localhost:5000/api/success-stories?user_id=user_001&limit=5")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Test peer insights endpoint
print("\n\nTesting peer insights endpoint...")
response = requests.get("http://localhost:5000/api/peer-insights?user_id=user_001")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
