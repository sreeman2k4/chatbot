#!/usr/bin/env python3
"""
Direct Backend Testing Script
Tests the backend API endpoints directly to diagnose issues
"""

import requests
import json
import time
import sys

def test_backend_health():
    """Test if backend is running and healthy"""
    print("🔍 Testing Backend Health...")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   Status: {data.get('status')}")
            print(f"   Documents loaded: {data.get('documents_loaded')}")
            if 'ollama_status' in data:
                ollama = data['ollama_status']
                print(f"   Ollama: {ollama.get('status')} - {ollama.get('message')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection directly"""
    print("\n🔌 Testing Ollama Connection...")
    
    try:
        response = requests.get("http://localhost:8000/api/chatbot/ollama-test", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama test result:")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            if 'response_time' in data:
                print(f"   Response time: {data.get('response_time'):.2f}s")
            return data.get('status') == 'healthy'
        else:
            print(f"❌ Ollama test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama test error: {e}")
        return False

def test_instant_math():
    """Test instant math responses"""
    print("\n🧮 Testing Instant Math...")
    
    math_queries = ["7+4", "10*5", "100/4", "2^3"]
    
    for query in math_queries:
        print(f"\n📊 Testing: {query}")
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=10  # 10 second timeout for testing
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = end_time - start_time
                print(f"✅ Success! ({response_time:.3f}s)")
                print(f"   Response: {data['response'][:100]}...")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
                print(f"   Model: {data['metadata'].get('model', 'unknown')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after 10 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_instant_greetings():
    """Test instant greeting responses"""
    print("\n👋 Testing Instant Greetings...")
    
    greeting_queries = ["hello", "hi", "help", "what can you do"]
    
    for query in greeting_queries:
        print(f"\n💬 Testing: {query}")
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = end_time - start_time
                print(f"✅ Success! ({response_time:.3f}s)")
                print(f"   Response: {data['response'][:100]}...")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after 10 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_complex_rag():
    """Test complex RAG queries"""
    print("\n🧠 Testing Complex RAG...")
    
    complex_queries = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "How does NLP work?"
    ]
    
    for query in complex_queries:
        print(f"\n🤔 Testing: {query}")
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=20  # Longer timeout for complex queries
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = end_time - start_time
                print(f"✅ Success! ({response_time:.3f}s)")
                print(f"   Response: {data['response'][:150]}...")
                print(f"   Sources: {len(data['sources'])}")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after 20 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chatbot_stats():
    """Test chatbot service statistics"""
    print("\n📊 Testing Chatbot Stats...")
    
    try:
        response = requests.get("http://localhost:8000/api/chatbot/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot stats:")
            print(f"   Documents: {data.get('documents_count')}")
            print(f"   Embeddings loaded: {data.get('embeddings_loaded')}")
            print(f"   Default model: {data.get('default_model')}")
            print(f"   Optimization: {data.get('optimization')}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def test_face_recognition():
    """Test face recognition service"""
    print("\n📷 Testing Face Recognition...")
    
    try:
        response = requests.get("http://localhost:8000/api/face/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Face recognition stats:")
            print(f"   Registered users: {data.get('registered_users', 0)}")
            print(f"   Service status: {data.get('service_status', 'unknown')}")
        else:
            print(f"❌ Face recognition failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Face recognition error: {e}")

def main():
    """Main test function"""
    print("🚀 Direct Backend Testing")
    print("=" * 60)
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n❌ Backend is not healthy. Please start the backend first.")
        print("   Command: cd backend && uvicorn app:app --reload --host 127.0.0.1 --port 8000")
        return
    
    # Test 2: Ollama connection
    ollama_healthy = test_ollama_connection()
    
    # Test 3: Chatbot stats
    test_chatbot_stats()
    
    # Test 4: Face recognition
    test_face_recognition()
    
    # Test 5: Instant responses (should work regardless of Ollama)
    test_instant_math()
    test_instant_greetings()
    
    # Test 6: Complex RAG (depends on Ollama)
    if ollama_healthy:
        test_complex_rag()
    else:
        print("\n⚠️  Skipping complex RAG tests - Ollama is not healthy")
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")
    
    if not ollama_healthy:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Check if Ollama is running: ollama list")
        print("2. Restart Ollama service")
        print("3. Check Ollama logs for errors")
        print("4. Verify model is downloaded: ollama pull mistral:7b")

if __name__ == "__main__":
    main()

