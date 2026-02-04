"""
Quick Response Time Test - Versi Sederhana
Jalankan script ini untuk testing cepat response time
"""
import requests
import time

BASE_URL = "http://127.0.0.1:5500"

def quick_test():
    print("\n" + "="*50)
    print("QUICK RESPONSE TIME TEST")
    print("="*50 + "\n")
    
    # Test 1: Start Conversation
    print("1. Testing Start Conversation...")
    times = []
    for i in range(5):
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/start_conversation", json={})
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"   Attempt {i+1}: {elapsed:.4f}s")
    
    avg_start = sum(times) / len(times)
    print(f"   Average: {avg_start:.4f}s\n")
    
    # Test 2: Send Message
    print("2. Testing Send Message...")
    queries = [
        "pizza",
        "pizza di kuta",
        "restoran italia dengan wifi",
        "tempat makan romantis untuk dinner date"
    ]
    
    times = []
    for query in queries:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/send_message",
            json={"message": query}
        )
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"   '{query[:30]}': {elapsed:.4f}s")
        time.sleep(0.3)  # Small delay
    
    avg_message = sum(times) / len(times)
    print(f"   Average: {avg_message:.4f}s\n")
    
    # Summary
    print("="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Start Conversation Avg: {avg_start:.4f}s")
    print(f"Send Message Avg:       {avg_message:.4f}s")
    print(f"Total Avg:              {(avg_start + avg_message) / 2:.4f}s")
    
    if avg_message < 1.0:
        print("\n✓ EXCELLENT - Response time < 1 second")
    elif avg_message < 2.0:
        print("\n✓ GOOD - Response time < 2 seconds")
    else:
        print("\n⚠ WARNING - Response time > 2 seconds")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        quick_test()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Make sure the backend is running at http://127.0.0.1:5500")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
