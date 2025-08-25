#!/usr/bin/env python3
"""
Test script for the improved chatbot with conversation memory
"""

import requests
import json
import time

def test_conversation_memory():
    """Test conversation memory and personal information"""
    print("🧠 Testing Conversation Memory...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Tell the bot your name
    print("\n👤 Test 1: Telling bot your name")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "my name is sreeman",
                "chat_history": [],
                "settings": {}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Ask what your name is
    print("\n❓ Test 2: Asking what your name is")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "what is my name",
                "chat_history": [],
                "settings": {}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Ask about yourself
    print("\n🤔 Test 3: Asking what the bot knows about you")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "what do you know about me",
                "chat_history": [],
                "settings": {}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_instant_responses():
    """Test instant responses"""
    print("\n⚡ Testing Instant Responses...")
    
    base_url = "http://localhost:8000"
    
    # Test math
    print("\n🧮 Testing math: 7+4")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "7+4",
                "chat_history": [],
                "settings": {}
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test greeting
    print("\n👋 Testing greeting: hi")
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
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_complex_queries():
    """Test complex queries with RAG"""
    print("\n🔍 Testing Complex RAG Queries...")
    
    base_url = "http://localhost:8000"
    
    queries = [
        "what is artificial intelligence",
        "explain gravity",
        "how does machine learning work"
    ]
    
    for query in queries:
        print(f"\n🤔 Testing: {query}")
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:150]}...")
                print(f"   Sources: {len(data['sources'])}")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chatbot_stats():
    """Test chatbot statistics"""
    print("\n📊 Testing Chatbot Stats...")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/chatbot/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot stats:")
            print(f"   Documents: {data.get('documents_count')}")
            print(f"   Optimization: {data.get('optimization')}")
            print(f"   Conversations stored: {data.get('conversations_stored')}")
            print(f"   Users remembered: {data.get('users_remembered')}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Improved Chatbot with Conversation Memory")
    print("=" * 70)
    
    # Test 1: Conversation memory
    test_conversation_memory()
    
    # Test 2: Instant responses
    test_instant_responses()
    
    # Test 3: Complex queries
    test_complex_queries()
    
    # Test 4: Stats
    test_chatbot_stats()
    
    print("\n" + "=" * 70)
    print("✅ Testing completed!")
    print("\n💡 The chatbot should now:")
    print("   • Remember your name and personal info")
    print("   • Give instant responses to math and greetings")
    print("   • Handle complex queries with retry logic")
    print("   • Save conversation memory to file")

if __name__ == "__main__":
    main()

