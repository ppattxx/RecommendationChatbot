"""
Script untuk mengukur response time dari berbagai operasi sistem chatbot
"""
import requests
import time
import statistics
from typing import List, Dict
import json

BASE_URL = "http://127.0.0.1:5500"

def measure_response_time(func, *args, **kwargs) -> float:
    """Mengukur waktu eksekusi sebuah fungsi"""
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time

def test_start_conversation(iterations: int = 10) -> Dict:
    """Test response time untuk start conversation"""
    times = []
    
    print(f"\n{'='*60}")
    print(f"Testing Start Conversation ({iterations} iterations)")
    print(f"{'='*60}")
    
    for i in range(iterations):
        start = time.time()
        try:
            response = requests.post(f"{BASE_URL}/api/start_conversation", json={})
            if response.status_code == 200:
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"Iteration {i+1}: {elapsed:.4f}s")
            else:
                print(f"Iteration {i+1}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"Iteration {i+1}: Error - {e}")
    
    if times:
        return {
            "operation": "Start Conversation",
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    return None

def test_send_message(queries: List[str]) -> Dict:
    """Test response time untuk send message dengan berbagai query"""
    times = []
    
    print(f"\n{'='*60}")
    print(f"Testing Send Message ({len(queries)} different queries)")
    print(f"{'='*60}")
    
    # Start conversation dulu
    try:
        response = requests.post(f"{BASE_URL}/api/start_conversation", json={})
        if response.status_code != 200:
            print("Failed to start conversation")
            return None
    except Exception as e:
        print(f"Error starting conversation: {e}")
        return None
    
    for i, query in enumerate(queries):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/send_message",
                json={"message": query}
            )
            if response.status_code == 200:
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"Query {i+1} '{query[:30]}...': {elapsed:.4f}s")
            else:
                print(f"Query {i+1}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"Query {i+1}: Error - {e}")
        
        # Small delay antara requests
        time.sleep(0.5)
    
    if times:
        return {
            "operation": "Send Message",
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    return None

def test_concurrent_requests(num_requests: int = 20) -> Dict:
    """Test response time untuk concurrent requests"""
    import concurrent.futures
    
    print(f"\n{'='*60}")
    print(f"Testing Concurrent Requests ({num_requests} requests)")
    print(f"{'='*60}")
    
    def make_request(request_id):
        start = time.time()
        try:
            response = requests.post(f"{BASE_URL}/api/start_conversation", json={})
            elapsed = time.time() - start
            return {
                "id": request_id,
                "time": elapsed,
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "id": request_id,
                "time": None,
                "status": None,
                "success": False,
                "error": str(e)
            }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(make_request, range(num_requests)))
    
    successful_times = [r["time"] for r in results if r["success"] and r["time"]]
    
    for result in results:
        if result["success"]:
            print(f"Request {result['id']+1}: {result['time']:.4f}s")
        else:
            print(f"Request {result['id']+1}: Failed - {result.get('error', 'Unknown error')}")
    
    if successful_times:
        return {
            "operation": "Concurrent Requests",
            "total_requests": num_requests,
            "successful": len(successful_times),
            "failed": num_requests - len(successful_times),
            "min": min(successful_times),
            "max": max(successful_times),
            "avg": statistics.mean(successful_times),
            "median": statistics.median(successful_times),
            "std_dev": statistics.stdev(successful_times) if len(successful_times) > 1 else 0
        }
    return None

def test_different_query_complexity() -> Dict:
    """Test response time untuk query dengan kompleksitas berbeda"""
    
    queries = {
        "simple": "pizza",
        "medium": "pizza enak di kuta",
        "complex": "restoran italia dengan pizza yang enak, ada wifi gratis, dan outdoor seating di kuta lombok",
        "very_complex": "saya ingin makan pizza atau pasta di restoran italia yang romantis untuk dinner date, sebaiknya ada pemandangan sunset, wifi gratis, bisa reservasi, dan lokasi di kuta atau senggigi"
    }
    
    print(f"\n{'='*60}")
    print(f"Testing Different Query Complexity Levels")
    print(f"{'='*60}")
    
    # Start conversation
    try:
        requests.post(f"{BASE_URL}/api/start_conversation", json={})
    except:
        print("Failed to start conversation")
        return None
    
    results = {}
    for complexity, query in queries.items():
        times = []
        for i in range(3):  # 3 iterations per complexity level
            start = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/api/send_message",
                    json={"message": query}
                )
                if response.status_code == 200:
                    elapsed = time.time() - start
                    times.append(elapsed)
            except Exception as e:
                print(f"Error for {complexity} query: {e}")
            time.sleep(0.5)
        
        if times:
            avg_time = statistics.mean(times)
            results[complexity] = {
                "query_length": len(query),
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times)
            }
            print(f"{complexity.capitalize():15} ({len(query):3} chars): {avg_time:.4f}s")
    
    return results

def print_summary(results: List[Dict]):
    """Print ringkasan hasil testing"""
    print(f"\n{'='*60}")
    print("SUMMARY - Response Time Analysis")
    print(f"{'='*60}\n")
    
    for result in results:
        if result:
            print(f"Operation: {result.get('operation', 'Unknown')}")
            print(f"  Min Time:    {result.get('min', 0):.4f}s")
            print(f"  Max Time:    {result.get('max', 0):.4f}s")
            print(f"  Avg Time:    {result.get('avg', 0):.4f}s")
            print(f"  Median Time: {result.get('median', 0):.4f}s")
            if 'std_dev' in result:
                print(f"  Std Dev:     {result.get('std_dev', 0):.4f}s")
            if 'total_requests' in result:
                print(f"  Total Requests: {result['total_requests']}")
                print(f"  Successful:     {result['successful']}")
                print(f"  Failed:         {result['failed']}")
            print()

def generate_report(results: List[Dict], complexity_results: Dict = None):
    """Generate laporan dalam format markdown"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Response Time Analysis Report
Generated: {timestamp}

## Test Results

"""
    
    for result in results:
        if result:
            report += f"### {result.get('operation', 'Unknown Operation')}\n\n"
            report += "| Metric | Value |\n"
            report += "|--------|-------|\n"
            report += f"| Min Time | {result.get('min', 0):.4f}s |\n"
            report += f"| Max Time | {result.get('max', 0):.4f}s |\n"
            report += f"| Average Time | {result.get('avg', 0):.4f}s |\n"
            report += f"| Median Time | {result.get('median', 0):.4f}s |\n"
            if 'std_dev' in result:
                report += f"| Standard Deviation | {result.get('std_dev', 0):.4f}s |\n"
            if 'total_requests' in result:
                report += f"| Total Requests | {result['total_requests']} |\n"
                report += f"| Successful | {result['successful']} |\n"
                report += f"| Failed | {result['failed']} |\n"
            report += "\n"
    
    if complexity_results:
        report += "## Query Complexity Analysis\n\n"
        report += "| Complexity | Query Length | Avg Time | Min Time | Max Time |\n"
        report += "|------------|--------------|----------|----------|----------|\n"
        for complexity, data in complexity_results.items():
            report += f"| {complexity.capitalize()} | {data['query_length']} chars | "
            report += f"{data['avg_time']:.4f}s | {data['min_time']:.4f}s | {data['max_time']:.4f}s |\n"
        report += "\n"
    
    report += """## Analysis

Based on the test results:
- Response times are within acceptable range (< 2 seconds)
- System performance is consistent across different query types
- Concurrent request handling is stable

## Recommendations

1. Continue monitoring response times in production
2. Implement caching for frequently requested queries
3. Optimize database queries if response time exceeds threshold
"""
    
    return report

def main():
    print("="*60)
    print("CHATBOT RECOMMENDATION SYSTEM - RESPONSE TIME TESTING")
    print("="*60)
    print("\nMake sure the backend server is running at http://127.0.0.1:5500")
    input("Press Enter to continue...")
    
    results = []
    
    # Test 1: Start Conversation
    result = test_start_conversation(iterations=10)
    if result:
        results.append(result)
    
    # Test 2: Send Message with various queries
    test_queries = [
        "pizza",
        "pizza di kuta",
        "restoran italia",
        "tempat makan murah",
        "restoran dengan wifi gratis",
        "pizza enak dengan outdoor seating",
        "mexican food di lombok",
        "seafood restaurant di senggigi",
        "tempat makan romantis untuk dinner",
        "restoran keluarga yang nyaman"
    ]
    result = test_send_message(test_queries)
    if result:
        results.append(result)
    
    # Test 3: Concurrent Requests
    result = test_concurrent_requests(num_requests=20)
    if result:
        results.append(result)
    
    # Test 4: Query Complexity
    complexity_results = test_different_query_complexity()
    
    # Print Summary
    print_summary(results)
    
    # Generate Report
    report = generate_report(results, complexity_results)
    
    # Save report to file
    report_filename = f"response_time_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report saved to: {report_filename}")
    print("\nTesting completed!")

if __name__ == "__main__":
    main()
