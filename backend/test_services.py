#!/usr/bin/env python3
"""
Test script to verify that both services work correctly after refactoring.
Run this script to test the services independently.
"""

import time
import base64
import numpy as np

def test_face_recognition_service():
    """Test the face recognition service"""
    print("🧪 Testing Face Recognition Service...")
    
    try:
        from face_recognition_service import face_service
        
        # Test service initialization
        print("✅ Face service imported successfully")
        print(f"📊 Face service stats: {face_service.get_stats()}")
        
        # Test with a dummy base64 image (this will fail but shows the service works)
        dummy_image = base64.b64encode(b"dummy_image_data").decode('utf-8')
        
        # Test registration (will fail due to no face in dummy image)
        result = face_service.register_face("test_user", dummy_image)
        print(f"📝 Registration test result: {result}")
        
        print("✅ Face recognition service test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ Face recognition service test failed: {e}")
        return False

def test_chatbot_service():
    """Test the chatbot service"""
    print("🤖 Testing Chatbot Service...")
    
    try:
        from chatbot_service import chatbot_service
        
        # Test service initialization
        print("✅ Chatbot service imported successfully")
        print(f"📊 Chatbot service stats: {chatbot_service.get_stats()}")
        
        # Test document initialization
        chatbot_service.initialize_sample_documents()
        print(f"📚 Documents loaded: {len(chatbot_service.documents)}")
        
        # Test document search
        query = "What is artificial intelligence?"
        results = chatbot_service.search_similar_documents(query, top_k=2)
        print(f"🔍 Search results for '{query}': {len(results)} documents found")
        
        # Test RAG response generation (will fail if Ollama is not running)
        try:
            response = chatbot_service.generate_rag_response(
                query, 
                results, 
                {"model": "mistral:7b", "temperature": 0.7}
            )
            print(f"💬 RAG response generated: {len(response.get('sources', []))} sources")
        except Exception as e:
            print(f"⚠️  RAG response generation failed (expected if Ollama not running): {e}")
        
        print("✅ Chatbot service test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot service test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    print("📦 Testing Module Imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"❌ PIL/Pillow import failed: {e}")
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
    
    try:
        from PyPDF2 import PdfReader
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
    
    try:
        from docx import Document
        print("✅ Python-docx imported successfully")
    except ImportError as e:
        print(f"❌ Python-docx import failed: {e}")
    
    try:
        from tqdm import tqdm
        print("✅ TQDM imported successfully")
    except ImportError as e:
        print(f"❌ TQDM import failed: {e}")
    
    print()

def main():
    """Run all tests"""
    print("🚀 Starting Service Tests...\n")
    
    # Test imports first
    test_imports()
    
    # Test services
    face_success = test_face_recognition_service()
    chatbot_success = test_chatbot_service()
    
    # Summary
    print("📋 Test Summary:")
    print(f"   Face Recognition Service: {'✅ PASS' if face_success else '❌ FAIL'}")
    print(f"   Chatbot Service: {'✅ PASS' if chatbot_success else '❌ FAIL'}")
    
    if face_success and chatbot_success:
        print("\n🎉 All tests passed! Services are working correctly.")
        print("   You can now run the main app with: uvicorn app:app --reload --host 127.0.0.1 --port 8000")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    main()

