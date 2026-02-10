"""Test enhancements: DTO validation, error handling, request_id correlation."""
import requests
import json

base = 'http://127.0.0.1:5500'
results = []

# Test 1: DTO validation – empty body
print('=== TEST 1: POST /api/chat with empty body ===')
r = requests.post(f'{base}/api/chat', data='not json', headers={'Content-Type': 'text/plain'})
data = r.json()
print(f'  Status: {r.status_code} (expect 422)')
print(f'  Error: {data.get("error")}')
print(f'  Has request_id: {bool(data.get("request_id"))}')
results.append(('Empty body → 422', r.status_code == 422))

# Test 2: DTO validation – invalid page param
print('\n=== TEST 2: GET /api/recommendations?page=abc ===')
r = requests.get(f'{base}/api/recommendations?page=abc')
data = r.json()
print(f'  Status: {r.status_code} (expect 422)')
print(f'  Error: {data.get("error")}')
results.append(('Invalid page → 422', r.status_code == 422))

# Test 3: request_id in response header
print('\n=== TEST 3: Request ID correlation ===')
r = requests.get(f'{base}/api/recommendations/categories')
req_id = r.headers.get('X-Request-ID', '')
print(f'  X-Request-ID header: {req_id}')
print(f'  Has value: {bool(req_id)}')
results.append(('X-Request-ID present', bool(req_id)))

# Test 4: Custom request_id forwarded
print('\n=== TEST 4: Custom X-Request-ID forwarded ===')
custom_id = 'test-custom-12345'
r = requests.get(f'{base}/api/recommendations/categories', headers={'X-Request-ID': custom_id})
returned_id = r.headers.get('X-Request-ID', '')
print(f'  Sent: {custom_id}')
print(f'  Received: {returned_id}')
results.append(('Custom X-Request-ID forwarded', returned_id == custom_id))

# Test 5: 404 handler
print('\n=== TEST 5: 404 error handler ===')
r = requests.get(f'{base}/api/nonexistent')
data = r.json()
print(f'  Status: {r.status_code}')
print(f'  Has request_id: {bool(data.get("request_id"))}')
results.append(('404 with request_id', r.status_code == 404 and data.get('request_id') is not None))

# Test 6: Reset DTO validation – no identifiers
print('\n=== TEST 6: DELETE /api/chat/reset with no identifiers ===')
r = requests.delete(f'{base}/api/chat/reset', json={})
data = r.json()
print(f'  Status: {r.status_code} (expect 422)')
print(f'  Error: {data.get("error")}')
results.append(('Reset no ids → 422', r.status_code == 422))

# Summary
print('\n' + '=' * 50)
passed = sum(1 for _, ok in results if ok)
total = len(results)
for name, ok in results:
    status = 'PASS' if ok else 'FAIL'
    print(f'  {status} | {name}')
print(f'\nTotal: {passed}/{total} passed')
