#!/usr/bin/env python3
"""
Quick test script to verify the scraper endpoint works
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print(f"   Make sure the backend is running on {API_URL}")
        return False

def test_scrape_endpoint():
    """Test the scrape endpoint"""
    test_url = "https://tampa.craigslist.org/search/jjj"
    
    try:
        print(f"\nTesting scrape endpoint with URL: {test_url}")
        response = requests.post(
            f"{API_URL}/api/scrape",
            json={"url": test_url},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Scrape endpoint is working!")
            return True
        else:
            print(f"❌ Scrape endpoint returned error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - endpoint is not responding")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CL Monetizer API...")
    print("=" * 50)
    
    if not test_health():
        sys.exit(1)
    
    if not test_scrape_endpoint():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")

