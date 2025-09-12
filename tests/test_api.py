import requests
import json
BASE_URL = "http://127.0.0.1:8000"
def test_server_running():
    print("=== Testing Server Status ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Main page status: {response.status_code}")
        response = requests.get(f"{BASE_URL}/chat")
        print(f"Chat page status: {response.status_code}")
    except Exception as e:
        print(f"Server not running: {e}")
    print()
def test_health():
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()
def test_start_conversation():
    print("=== Testing Start Conversation ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/start_conversation",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
            return result.get('session_id')
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    return None
def test_send_message(session_id=None):
    print("=== Testing Send Message ===")
    payload = {
        'message': 'pizza di kuta'
    }
    if session_id:
        payload['session_id'] = session_id
    try:
        response = requests.post(
            f"{BASE_URL}/api/send_message",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()
if __name__ == "__main__":
    test_server_running()
    test_health()
    session_id = test_start_conversation()
    test_send_message(session_id)