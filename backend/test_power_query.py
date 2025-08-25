#!/usr/bin/env python3
"""
Test script for power query specifically
"""

import requests
import time

def test_power_query():
    """Test the power query specifically"""
    print("⚡ Testing Power Query")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test the power query
    print("\n🔍 Testing: 'what is power'")
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "what is power",
                "chat_history": [],
                "settings": {}
            },
            timeout=25
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_time = end_time - start_time
            print(f"✅ Success! ({response_time:.2f}s)")
            print(f"   Response: {data['response'][:200]}...")
            print(f"   Sources: {len(data['sources'])}")
            print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            print(f"   Model: {data['metadata'].get('model', 'unknown')}")
            
            # Show sources if available
            if data['sources']:
                print(f"\n📚 Sources found:")
                for i, source in enumerate(data['sources'], 1):
                    print(f"   {i}. {source.get('title', 'Unknown')}: {source.get('snippet', '')[:100]}...")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout after 25 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_related_queries():
    """Test related queries to see if knowledge base is working"""
    print("\n🔍 Testing Related Queries")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    queries = [
        "what is artificial intelligence",
        "explain gravity",
        "how does machine learning work"
    ]
    
    for query in queries:
        print(f"\n🤔 Testing: {query}")
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "chat_history": [],
                    "settings": {}
                },
                timeout=20
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = end_time - start_time
                print(f"✅ Success! ({response_time:.2f}s)")
                print(f"   Sources: {len(data['sources'])}")
                print(f"   Optimization: {data['metadata'].get('optimization', 'unknown')}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after 20 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🚀 Power Query Test")
    print("=" * 50)
    
    # Test 1: Power query specifically
    test_power_query()
    
    # Test 2: Related queries
    test_related_queries()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\n💡 Expected improvements:")
    print("   • Power query should now find relevant sources")
    print("   • Fallback responses should be more intelligent")
    print("   • Ollama timeouts should be shorter (5s, 10s, 15s)")
    print("   • Better knowledge base utilization")

if __name__ == "__main__":
    main()

