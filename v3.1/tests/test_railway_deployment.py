#!/usr/bin/env python
"""
Test Railway deployment end-to-end.
"""

import requests
import json
import time

RAILWAY_URL = "https://analytics-v30-production.up.railway.app"

def test_railway_deployment():
    """Test full chart generation on Railway."""
    print("=" * 70)
    print("  Testing Railway Deployment: analytics-v30-production.up.railway.app")
    print("=" * 70)
    print()

    # Test 1: Service Info
    print("📋 Test 1: Service Information")
    response = requests.get(f"{RAILWAY_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    # Test 2: Health Check
    print("❤️  Test 2: Health Check")
    response = requests.get(f"{RAILWAY_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    # Test 3: Chart Generation
    print("🚀 Test 3: Chart Generation")
    request_data = {
        "content": "Show monthly sales data for e-commerce store",
        "title": "2024 Monthly Sales Performance",
        "chart_type": "line",
        "theme": "professional"
    }

    print(f"📤 Submitting request: {request_data['title']}")
    response = requests.post(f"{RAILWAY_URL}/generate", json=request_data)
    result = response.json()

    job_id = result["job_id"]
    print(f"✅ Job created: {job_id}")
    print(f"   Status: {result['status']}")
    print()

    # Poll for completion
    print("⏳ Polling for results...")
    max_attempts = 30
    attempt = 0

    while attempt < max_attempts:
        time.sleep(2)
        attempt += 1

        status_response = requests.get(f"{RAILWAY_URL}/status/{job_id}")
        status = status_response.json()

        progress = status.get("progress", 0)
        stage = status.get("stage", "unknown")
        job_status = status["status"]

        print(f"  [{attempt:2d}] {job_status:12s} | {progress:3d}% | {stage}")

        if job_status == "completed":
            print()
            print("=" * 70)
            print("✅ DEPLOYMENT TEST SUCCESSFUL!")
            print("=" * 70)
            print()
            print("📊 Chart Details:")
            print(f"  URL: {status['chart_url']}")
            print(f"  Type: {status['chart_type']}")
            print(f"  Theme: {status['theme']}")
            print()
            print("📈 Chart Data:")
            print(json.dumps(status['chart_data'], indent=2))
            print()
            print("🔗 View Chart:")
            print(f"  {status['chart_url']}")
            print()
            print("=" * 70)
            return True

        elif job_status == "failed":
            print()
            print("❌ Chart generation failed!")
            print(f"Error: {status.get('error')}")
            return False

    print()
    print("⏱️ Timeout waiting for completion")
    return False

if __name__ == "__main__":
    try:
        success = test_railway_deployment()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
