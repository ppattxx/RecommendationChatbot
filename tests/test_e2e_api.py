"""End-to-end API test for the refactored backend."""
import requests
import json

base = 'http://127.0.0.1:5500'
results = []

# Test 1: Chat endpoint (greeting)
print('=== TEST 1: POST /api/chat (greeting) ===')
r = requests.post(f'{base}/api/chat', json={'message': 'halo', 'device_token': 'test_cleanup'})
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Success: {data.get("success")}')
sid = data.get('data', {}).get('session_id', '')
print(f'  Session: {sid[:20]}...')
results.append(('POST /api/chat (greeting)', r.status_code == 200 and data.get('success')))

# Test 2: Chat with message
print('\n=== TEST 2: POST /api/chat (message) ===')
r = requests.post(f'{base}/api/chat', json={'message': 'restoran di senggigi', 'session_id': sid, 'device_token': 'test_cleanup'})
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Success: {data.get("success")}')
bot_resp = data.get('data', {}).get('bot_response', '')
print(f'  Bot response length: {len(bot_resp)}')
results.append(('POST /api/chat (message)', r.status_code == 200 and data.get('success')))

# Test 3: Chat history
print('\n=== TEST 3: GET /api/chat/history ===')
r = requests.get(f'{base}/api/chat/history/{sid}')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Message count: {data.get("data", {}).get("message_count")}')
results.append(('GET /api/chat/history', r.status_code == 200 and data.get('success')))

# Test 4: Recommendations
print('\n=== TEST 4: GET /api/recommendations ===')
r = requests.get(f'{base}/api/recommendations?page=1&per_page=5')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Restaurants: {len(data.get("data", {}).get("restaurants", []))}')
print(f'  Total: {data.get("data", {}).get("total")}')
results.append(('GET /api/recommendations', r.status_code == 200 and data.get('success')))

# Test 5: Categories
print('\n=== TEST 5: GET /api/recommendations/categories ===')
r = requests.get(f'{base}/api/recommendations/categories')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Categories: {len(data.get("data", {}).get("categories", []))}')
results.append(('GET /api/recommendations/categories', r.status_code == 200 and data.get('success')))

# Test 6: Top 5
print('\n=== TEST 6: GET /api/recommendations/top5 ===')
r = requests.get(f'{base}/api/recommendations/top5?query=seafood+senggigi')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Algorithm: {data.get("data", {}).get("algorithm")}')
print(f'  Results: {len(data.get("data", {}).get("restaurants", []))}')
results.append(('GET /api/recommendations/top5', r.status_code == 200 and data.get('success')))

# Test 7: All ranked
print('\n=== TEST 7: GET /api/recommendations/all-ranked ===')
r = requests.get(f'{base}/api/recommendations/all-ranked?query=pizza&page=1&limit=5')
data = r.json()
print(f'  Status: {r.status_code}')
has_pagination = 'pagination' in data.get('data', {})
print(f'  Has pagination: {has_pagination}')
results.append(('GET /api/recommendations/all-ranked', r.status_code == 200 and data.get('success')))

# Test 8: Trending
print('\n=== TEST 8: GET /api/recommendations/trending ===')
r = requests.get(f'{base}/api/recommendations/trending?limit=3')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Results: {len(data.get("data", {}).get("restaurants", []))}')
results.append(('GET /api/recommendations/trending', r.status_code == 200 and data.get('success')))

# Test 9: User preferences
print('\n=== TEST 9: GET /api/user-preferences ===')
r = requests.get(f'{base}/api/user-preferences?device_token=test_cleanup')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Success: {data.get("success")}')
results.append(('GET /api/user-preferences', r.status_code == 200 and data.get('success')))

# Test 10: Preferences summary
print('\n=== TEST 10: GET /api/user-preferences/summary ===')
r = requests.get(f'{base}/api/user-preferences/summary')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Success: {data.get("success")}')
results.append(('GET /api/user-preferences/summary', r.status_code == 200 and data.get('success')))

# Cleanup test data
print('\n=== CLEANUP: DELETE /api/chat/reset ===')
r = requests.delete(f'{base}/api/chat/reset', json={'device_token': 'test_cleanup'})
data = r.json()
print(f'  Status: {r.status_code}')
results.append(('DELETE /api/chat/reset', r.status_code == 200 and data.get('success')))

# Summary
print('\n' + '=' * 50)
passed = sum(1 for _, ok in results if ok)
total = len(results)
for name, ok in results:
    status = 'PASS' if ok else 'FAIL'
    print(f'  {status} | {name}')
print(f'\nTotal: {passed}/{total} passed')
