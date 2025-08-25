#!/usr/bin/env python3
"""
Test script for Text Extraction API endpoints
"""

import requests
import base64
import time

def test_api_endpoints():
    """Test the text extraction API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Text Extraction API Endpoints")
    print("=" * 50)
    
    # Test 1: Service Status
    print("\n🔍 Test 1: Service Status")
    try:
        response = requests.get(f"{base_url}/api/extract-text/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"   Available Engines: {data.get('available_engines')}")
            print(f"   Supported Formats: {data.get('supported_formats')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Available Engines
    print("\n🔍 Test 2: Available Engines")
    try:
        response = requests.get(f"{base_url}/api/extract-text/engines", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Engines: {data.get('engines')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Health Check
    print("\n🔍 Test 3: Health Check")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status')}")
            print(f"   Ollama: {data.get('ollama_status', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API endpoint testing completed!")
    print("\n💡 To test text extraction:")
    print("   1. Start the backend: uvicorn app:app --reload --host 127.0.0.1 --port 8000")
    print("   2. Use the frontend to upload an image")
    print("   3. Or test directly with: curl -X POST /api/extract-text")

if __name__ == "__main__":
    test_api_endpoints()

