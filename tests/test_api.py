"""Test script for API endpoints"""
import sys
import time
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Response: {data}")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_root_endpoint():
    """Test root endpoint"""
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Response: {data}")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_upload_endpoint():
    """Test upload endpoint with sample PDF"""
    print("\n3. Testing upload endpoint...")
    try:
        pdf_path = Path("data/contracts/sample.pdf")
        if not pdf_path.exists():
            print(f"   ✗ Sample PDF not found at {pdf_path}")
            return False

        with open(pdf_path, 'rb') as f:
            files = {'file': ('sample.pdf', f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/api/v1/upload",
                files=files,
                timeout=60
            )

        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Filename: {data.get('filename')}")
            print(f"   ✓ Chunks created: {data.get('chunks_created')}")
            print(f"   ✓ Pages processed: {data.get('pages_processed')}")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_query_endpoint():
    """Test query endpoint"""
    print("\n4. Testing query endpoint...")
    try:
        payload = {
            "question": "What are the termination conditions?",
            "top_k": 4
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Question: {data.get('question')}")
            print(f"   ✓ Answer length: {len(data.get('answer', ''))} chars")
            print(f"   ✓ Sources: {len(data.get('sources', []))} chunks")
            print(f"   ✓ Latency: {data.get('latency_sec')}s")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n5. Testing error handling...")

    # Test invalid query (empty question)
    print("   a) Testing validation error...")
    try:
        payload = {"question": ""}  # Invalid: too short
        response = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json=payload,
            timeout=10
        )

        if response.status_code == 422:
            data = response.json()
            print(f"      ✓ Validation error caught: {response.status_code}")
            print(f"      ✓ Error type: {data.get('error')}")
            return True
        else:
            print(f"      ✗ Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False


def test_openapi_docs():
    """Test OpenAPI documentation endpoints"""
    print("\n6. Testing OpenAPI documentation...")
    try:
        response = requests.get(f"{BASE_URL}/api/openapi.json", timeout=5)
        if response.status_code == 200:
            print(f"   ✓ OpenAPI spec available at /api/openapi.json")
            print(f"   ✓ Docs available at /api/docs")
            return True
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("API ENDPOINT TESTS")
    print("=" * 60)

    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("Server is ready!")
            break
        except:
            time.sleep(1)
            print(f"Waiting... ({i+1}/10)")
    else:
        print("ERROR: Server not responding. Please start the server first:")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)

    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("Upload Endpoint", test_upload_endpoint()))
    results.append(("Query Endpoint", test_query_endpoint()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("OpenAPI Docs", test_openapi_docs()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if all(p for _, p in results) else 1


if __name__ == "__main__":
    sys.exit(main())
