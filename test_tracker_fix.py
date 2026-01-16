import requests

# Test if saving to tracker uses correct user_id
user_id = "user_001"

print(f"Testing application save/fetch for user: {user_id}")

# Test 1: Save an application
print("\n1. Creating application...")
save_response = requests.post("http://localhost:5000/api/applications", json={
    "user_id": user_id,
    "opportunity_title": "Test Internship",
    "opportunity_link": "https://example.com",
    "deadline": "2026-02-01",
    "eligibility_score": 85,
    "priority": "high",
    "notes": "Test application"
})

print(f"Status: {save_response.status_code}")
if save_response.ok:
    data = save_response.json()
    print(f"Created application: {data.get('application_id')}")
else:
    print(f"Error: {save_response.text}")

# Test 2: Fetch applications
print(f"\n2. Fetching applications for user {user_id}...")
fetch_response = requests.get(f"http://localhost:5000/api/applications/{user_id}")

print(f"Status: {fetch_response.status_code}")
if fetch_response.ok:
    apps = fetch_response.json()
    print(f"Found {len(apps)} applications:")
    for app in apps:
        print(f"  - {app.get('opportunity_title')} (ID: {app.get('id')})")
else:
    print(f"Error: {fetch_response.text}")

# Test 3: Track gamification action
print(f"\n3. Tracking gamification action...")
gami_response = requests.post("http://localhost:5000/api/gamification/action", json={
    "user_id": user_id,
    "action": "save_to_tracker",
    "metadata": {"opportunity_id": "test_123", "title": "Test Internship"}
})

print(f"Status: {gami_response.status_code}")
if gami_response.ok:
    data = gami_response.json()
    print(f"Points earned: {data.get('points_earned')}")
    print(f"New total points: {data.get('new_points')}")
else:
    print(f"Error: {gami_response.text}")
