import time
import requests
def test_chat_flow():
    base_url = "http://127.0.0.1:8000"
    print("=== TESTING COMPLETE CHAT FLOW ===")
    print("1. Starting conversation...")
    response = requests.post(f"{base_url}/api/start_conversation", json={})
    if response.status_code != 200:
        print(f"Failed to start conversation: {response.status_code}")
        return
    data = response.json()
    session_id = data.get('session_id')
    print(f"Conversation started. Session ID: {session_id}")
    print(f"Greeting: {data.get('greeting')[:50]}...")
    print("\n2. Sending first message...")
    message1 = "pizza enak di kuta"
    response = requests.post(
        f"{base_url}/api/send_message",
        json={"message": message1}
    )
    if response.status_code != 200:
        print(f"Failed to send message: {response.status_code}")
        print(f"Response: {response.text}")
        return
    data = response.json()
    print(f"Message sent successfully")
    print(f"Bot response: {data.get('response')[:100]}...")
    print("\n3. Sending follow-up message...")
    message2 = "yang murah saja"
    response = requests.post(
        f"{base_url}/api/send_message",
        json={"message": message2}
    )
    if response.status_code != 200:
        print(f"Failed to send follow-up: {response.status_code}")
        return
    data = response.json()
    print(f"Follow-up sent successfully")
    print(f"Bot response: {data.get('response')[:100]}...")
    print("\nCHAT FLOW TEST COMPLETED SUCCESSFULLY!")
    print("\nIf the test above works, then your chat API is functioning properly.")
    print("If you still can't send messages in the browser, try:")
    print("1. Open browser developer tools (F12)")
    print("2. Check Console tab for JavaScript errors")
    print("3. Check Network tab to see if API calls are being made")
if __name__ == "__main__":
    test_chat_flow()