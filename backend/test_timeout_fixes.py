#!/usr/bin/env python3
"""
Test script to verify timeout fixes in the chatbot service
"""

import requests
import json
import time

def test_instant_responses():
    """Test instant responses for simple queries"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Instant Responses...")
    
    # Test math queries
    math_queries = ["6+9", "10*5", "100/4"]
    for query in math_queries:
        print(f"\n📊 Testing math: {query}")
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Math response: {data['response'][:100]}...")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Math failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Math error: {e}")
    
    # Test simple greetings
    greeting_queries = ["hello", "hi", "help"]
    for query in greeting_queries:
        print(f"\n👋 Testing greeting: {query}")
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Greeting response: {data['response'][:100]}...")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Greeting failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Greeting error: {e}")

def test_ollama_health():
    """Test Ollama connection health"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing Ollama Health...")
    
    try:
        response = requests.get(f"{base_url}/api/chatbot/ollama-test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama status: {data['status']}")
            print(f"   Message: {data['message']}")
            if 'response_time' in data:
                print(f"   Response time: {data['response_time']:.2f}s")
        else:
            print(f"❌ Ollama test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama test error: {e}")

def test_complex_query():
    """Test a complex query that should use RAG"""
    base_url = "http://localhost:8000"
    
    print("\n🧠 Testing Complex RAG Query...")
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "What is artificial intelligence?",
                "chat_history": [],
                "settings": {}
            },
            timeout=20  # Longer timeout for complex queries
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Complex response: {data['response'][:150]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Complex query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Complex query error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Chatbot Timeout Fixes")
    print("=" * 50)
    
    # Test instant responses first
    test_instant_responses()
    
    # Test Ollama health
    test_ollama_health()
    
    # Test complex query
    test_complex_query()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

