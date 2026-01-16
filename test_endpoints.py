"""Test success stories and peer insights endpoints"""
import requests
import json

print("Testing Success Stories and Peer Insights Endpoints\n")
print("="*70)

# Test 1: Success Stories
print("\n1. Testing /api/success-stories endpoint:")
url1 = "http://localhost:5000/api/success-stories?user_id=user_001&limit=5"
try:
    response = requests.get(url1)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Success! Found {data['count']} stories")
        if data['stories']:
            print(f"   First story: {data['stories'][0]['name']} from {data['stories'][0]['college']}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 2: Peer Insights
print("\n2. Testing /api/peer-insights endpoint:")
url2 = "http://localhost:5000/api/peer-insights?user_id=user_001"
try:
    response = requests.get(url2)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Success!")
        insights = data['insights']
        print(f"   Your Points: {insights['your_stats']['points']}")
        print(f"   College Avg: {insights['peer_averages']['same_college']['points']}")
        print(f"   Insights: {len(insights['insights'])} recommendations")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 3: Analytics Insights (verify fix)
print("\n3. Testing /api/analytics/insights/user_001 endpoint:")
url3 = "http://localhost:5000/api/analytics/insights/user_001"
try:
    response = requests.get(url3)
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ Success! Found {len(data)} insights")
        if data:
            print(f"   Example: {data[0]['message']}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "="*70)
