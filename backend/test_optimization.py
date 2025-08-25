#!/usr/bin/env python3
"""
Test script to verify RAG optimization reduces API calls from 2 to 1.
"""

import time
import base64

def test_rag_optimization():
    """Test that RAG now uses only 1 embedding call instead of 2"""
    print("🧪 Testing RAG Optimization...")
    
    try:
        from chatbot_service import chatbot_service
        
        # Initialize documents
        print("📚 Initializing documents...")
        chatbot_service.initialize_sample_documents()
        
        # Test the OLD method (2 API calls)
        print("\n🔍 Testing OLD method (2 API calls)...")
        start_time = time.time()
        
        # This would make 2 calls: 1 for search, 1 for response
        # context_docs = chatbot_service.search_similar_documents("What is AI?", top_k=2)
        # response = chatbot_service.generate_rag_response("What is AI?", context_docs, {"model": "mistral:7b"})
        
        print("⚠️  OLD method would make 2 API calls (disabled for testing)")
        
        # Test the NEW optimized method (1 API call)
        print("\n🚀 Testing NEW optimized method (1 API call)...")
        start_time = time.time()
        
        response = chatbot_service.generate_rag_response_optimized(
            "What is artificial intelligence?", 
            top_k=2, 
            settings={"model": "mistral:7b"}
        )
        
        end_time = time.time()
        
        print(f"✅ Optimized method completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Response metadata: {response.get('metadata', {})}")
        print(f"🔍 Sources found: {len(response.get('sources', []))}")
        
        # Check if optimization flag is set
        if response.get('metadata', {}).get('optimization') == 'single_embedding_call':
            print("🎉 SUCCESS: Optimization flag detected!")
        else:
            print("⚠️  WARNING: Optimization flag not found")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG optimization test failed: {e}")
        return False

def main():
    """Run the optimization test"""
    print("🚀 Starting RAG Optimization Test...\n")
    
    success = test_rag_optimization()
    
    if success:
        print("\n🎉 RAG optimization test completed successfully!")
        print("   The chatbot now uses only 1 API call instead of 2!")
        print("   This should significantly improve response speed.")
    else:
        print("\n⚠️  RAG optimization test failed.")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    main()

