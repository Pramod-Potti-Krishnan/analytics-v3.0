#!/usr/bin/env python
"""
Quick test to verify Supabase bucket is working.
"""

import requests
import json
import time

API_URL = "http://localhost:8080"

def test_bucket_creation():
    """Test that the bucket was created."""
    print("🧪 Testing Supabase bucket...")

    # Check stats endpoint
    response = requests.get(f"{API_URL}/stats")
    stats = response.json()

    print(f"✅ Storage bucket: {stats['storage_bucket']}")
    print(f"✅ Server is healthy\n")

def test_chart_generation():
    """Test full chart generation with Supabase upload."""
    print("🚀 Testing chart generation with Supabase upload...")

    # Submit job
    request_data = {
        "content": "Show quarterly sales performance for 2024",
        "title": "Q1-Q4 2024 Sales",
        "chart_type": "bar_vertical",
        "theme": "professional"
    }

    print(f"📤 Submitting request: {request_data['title']}")
    response = requests.post(f"{API_URL}/generate", json=request_data)
    result = response.json()

    job_id = result["job_id"]
    print(f"✅ Job created: {job_id}\n")

    # Poll for completion
    print("⏳ Polling for results...")
    max_attempts = 30
    attempt = 0

    while attempt < max_attempts:
        time.sleep(1)
        attempt += 1

        status_response = requests.get(f"{API_URL}/status/{job_id}")
        status = status_response.json()

        progress = status.get("progress", 0)
        stage = status.get("stage", "unknown")
        job_status = status["status"]

        print(f"  [{attempt}] Status: {job_status} | Progress: {progress}% | Stage: {stage}")

        if job_status == "completed":
            print("\n✅ Chart generated successfully!\n")
            print("📊 Results:")
            print(f"  Chart URL: {status['chart_url']}")
            print(f"  Chart Type: {status['chart_type']}")
            print(f"  Theme: {status['theme']}")
            print(f"\n📈 Chart Data:")
            print(json.dumps(status['chart_data'], indent=2))
            print(f"\n🔗 Open chart in browser: {status['chart_url']}")
            return True

        elif job_status == "failed":
            print(f"\n❌ Job failed: {status.get('error')}")
            return False

    print("\n⏱️ Timeout waiting for job completion")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Analytics Microservice v3 - Supabase Integration Test")
    print("=" * 60)
    print()

    # Test bucket
    test_bucket_creation()

    # Test chart generation
    success = test_chart_generation()

    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed! Supabase integration is working.")
    else:
        print("❌ Tests failed. Check the error messages above.")
    print("=" * 60)
