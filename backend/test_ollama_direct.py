#!/usr/bin/env python3
"""
Direct Ollama Connection Test
Tests Ollama API directly to diagnose timeout issues
"""

import requests
import time
import json

def test_ollama_direct():
    """Test Ollama API directly"""
    print("🔌 Testing Ollama API Directly")
    print("=" * 50)
    
    base_url = "http://localhost:11434"
    
    # Test 1: Basic connection
    print("\n📡 Test 1: Basic Connection")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            models = response.json().get("models", [])
            print(f"   Available models: {[m['name'] for m in models]}")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False
    
    # Test 2: Simple generation with short timeout
    print("\n🧠 Test 2: Simple Generation (5s timeout)")
    try:
        payload = {
            "model": "mistral:7b",
            "prompt": "Hello",
            "stream": False,
            "options": {
                "num_predict": 10
            }
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=5
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ Generation successful in {end_time - start_time:.2f}s")
            data = response.json()
            print(f"   Response: {data.get('response', '')[:50]}...")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout after 5 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Generation with longer timeout
    print("\n🧠 Test 3: Generation (15s timeout)")
    try:
        payload = {
            "model": "mistral:7b",
            "prompt": "What is artificial intelligence?",
            "stream": False,
            "options": {
                "num_predict": 50
            }
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=15
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ Generation successful in {end_time - start_time:.2f}s")
            data = response.json()
            print(f"   Response: {data.get('response', '')[:100]}...")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout after 15 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Check Ollama process
    print("\n🔍 Test 4: Ollama Process Check")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama CLI working")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ Ollama CLI error: {result.stderr}")
    except Exception as e:
        print(f"❌ Cannot run ollama list: {e}")
    
    return True

def test_backend_endpoint():
    """Test the backend endpoint"""
    print("\n🌐 Testing Backend Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            if 'ollama_status' in data:
                ollama = data['ollama_status']
                print(f"   Ollama: {ollama.get('status')} - {ollama.get('message')}")
        else:
            print(f"❌ Backend health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test chat endpoint with simple query
    print("\n💬 Test Chat Endpoint: 'hi'")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "hi",
                "chat_history": [],
                "settings": {}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # Test chat endpoint with complex query
    print("\n💬 Test Chat Endpoint: 'what is power'")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "what is power",
                "chat_history": [],
                "settings": {}
            },
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data['response'][:150]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat error: {e}")

def main():
    """Main test function"""
    print("🚀 Ollama Connection Diagnostics")
    print("=" * 60)
    
    # Test 1: Direct Ollama connection
    if test_ollama_direct():
        # Test 2: Backend endpoint
        test_backend_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostics completed!")
    print("\n🔧 Troubleshooting Tips:")
    print("1. Check if Ollama is running: ollama list")
    print("2. Check Ollama logs for errors")
    print("3. Verify model is downloaded: ollama pull mistral:7b")
    print("4. Check system resources (RAM, CPU)")
    print("5. Try restarting Ollama service")

if __name__ == "__main__":
    main()

