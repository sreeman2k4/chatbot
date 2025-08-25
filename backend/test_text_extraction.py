#!/usr/bin/env python3
"""
Test script for Text Extraction Service
Demonstrates OCR capabilities for both printed and handwritten text
"""

import os
import base64
from text_extraction_service import text_extraction_service

def test_service_status():
    """Test the service status"""
    print("🔍 Testing Service Status")
    print("=" * 40)
    
    status = text_extraction_service.get_service_status()
    print(f"Service: {status['service']}")
    print(f"Status: {status['status']}")
    print(f"Available Engines: {status['available_engines']}")
    print(f"Supported Formats: {status['supported_formats']}")
    print(f"Tesseract: {'✅' if status['tesseract_available'] else '❌'}")
    print(f"EasyOCR: {'✅' if status['easyocr_available'] else '❌'}")
    print(f"TrOCR: {'✅' if status['trocr_available'] else '❌'}")

def test_image_extraction(image_path: str):
    """Test text extraction from an image file"""
    print(f"\n🔍 Testing Image: {image_path}")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    # Test with different engines
    engines = ['auto', 'tesseract', 'easyocr', 'trocr']
    
    for engine in engines:
        if engine == 'tesseract' and not text_extraction_service.get_service_status()['tesseract_available']:
            print(f"⏭️  Skipping {engine} (not available)")
            continue
        if engine == 'easyocr' and not text_extraction_service.get_service_status()['easyocr_available']:
            print(f"⏭️  Skipping {engine} (not available)")
            continue
        if engine == 'trocr' and not text_extraction_service.get_service_status()['trocr_available']:
            print(f"⏭️  Skipping {engine} (not available)")
            continue
        
        print(f"\n🧠 Testing with {engine} engine:")
        print("-" * 30)
        
        try:
            result = text_extraction_service.extract_text_from_image(
                image_path, 
                engine=engine,
                preprocess=True,
                detect_regions=True
            )
            
            if result['success']:
                print(f"✅ Success!")
                print(f"   Engine used: {result['engine_used']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Regions detected: {len(result['regions'])}")
                print(f"   Text length: {len(result['text'])} characters")
                
                # Show text preview
                text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                print(f"   Text preview: {text_preview}")
                
                # Show detected regions
                if result['regions']:
                    print(f"   Text regions:")
                    for i, (x, y, w, h) in enumerate(result['regions'][:5], 1):  # Show first 5 regions
                        print(f"      {i}. Position: ({x}, {y}), Size: {w}x{h}")
                    if len(result['regions']) > 5:
                        print(f"      ... and {len(result['regions']) - 5} more regions")
                
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error testing {engine}: {e}")

def test_base64_extraction(image_path: str):
    """Test text extraction from base64 encoded image"""
    print(f"\n🔍 Testing Base64 Extraction: {image_path}")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    try:
        # Read image and convert to base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ Image converted to base64 ({len(base64_string)} characters)")
        
        # Test extraction
        result = text_extraction_service.extract_text_from_base64(
            base64_string,
            engine='auto',
            preprocess=True
        )
        
        if result['success']:
            print(f"✅ Base64 extraction successful!")
            print(f"   Engine used: {result['engine_used']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Text length: {len(result['text'])} characters")
            
            # Show text preview
            text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            print(f"   Text preview: {text_preview}")
        else:
            print(f"❌ Base64 extraction failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error testing base64 extraction: {e}")

def create_sample_text_image():
    """Create a sample image with text for testing"""
    try:
        import cv2
        import numpy as np
        
        # Create a white image
        img = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # Add some sample text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Sample Document", (50, 80), font, 1.5, (0, 0, 0), 2)
        cv2.putText(img, "This is a test document with printed text.", (50, 130), font, 0.8, (0, 0, 0), 2)
        cv2.putText(img, "It contains multiple lines of text for OCR testing.", (50, 160), font, 0.8, (0, 0, 0), 2)
        cv2.putText(img, "The text should be clearly readable by OCR engines.", (50, 190), font, 0.8, (0, 0, 0), 2)
        cv2.putText(img, "This helps verify the text extraction capabilities.", (50, 220), font, 0.8, (0, 0, 0), 2)
        
        # Add some handwritten-style text (simulated)
        cv2.putText(img, "Handwritten note:", (50, 280), font, 0.7, (100, 100, 100), 1)
        cv2.putText(img, "Meeting at 3 PM tomorrow", (50, 310), font, 0.6, (100, 100, 100), 1)
        cv2.putText(img, "Bring project documents", (50, 340), font, 0.6, (100, 100, 100), 1)
        
        # Save the image
        output_path = "sample_paper.jpg"
        cv2.imwrite(output_path, img)
        print(f"✅ Created sample image: {output_path}")
        return output_path
        
    except ImportError:
        print("⚠️  OpenCV not available, cannot create sample image")
        return None
    except Exception as e:
        print(f"❌ Error creating sample image: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Text Extraction Service Test")
    print("=" * 60)
    
    # Test 1: Service status
    test_service_status()
    
    # Test 2: Create sample image if needed
    sample_image = "sample_paper.jpg"
    if not os.path.exists(sample_image):
        print(f"\n📝 Creating sample image for testing...")
        sample_image = create_sample_text_image()
    
    # Test 3: Image extraction
    if sample_image and os.path.exists(sample_image):
        test_image_extraction(sample_image)
        
        # Test 4: Base64 extraction
        test_base64_extraction(sample_image)
    else:
        print(f"\n⚠️  No sample image available for testing")
        print("   Place an image file named 'sample_paper.jpg' in the backend directory")
        print("   Or the service will create one automatically if OpenCV is available")
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")
    print("\n💡 Usage examples:")
    print("   • Extract text from image: extract_text_from_image('paper.jpg')")
    print("   • Extract from base64: extract_text_from_base64(base64_string)")
    print("   • Choose engine: engine='tesseract', 'easyocr', 'trocr', or 'auto'")
    print("   • Enable preprocessing: preprocess=True")
    print("   • Detect text regions: detect_regions=True")

if __name__ == "__main__":
    main()

