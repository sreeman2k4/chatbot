#!/usr/bin/env python3
"""
Text Extraction Service for Papers and Documents
Supports both printed and handwritten text extraction using OCR
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import base64
from PIL import Image
import io

# Try to import OCR libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR available")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not available. Install with: pip install pytesseract")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ EasyOCR available")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not available. Install with: pip install easyocr")

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
    print("✅ PaddleOCR available")
except ImportError:
    PADDLE_AVAILABLE = False
    print("⚠️  PaddleOCR not available. Install with: pip install paddleocr")

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
    print("✅ TrOCR available")
except ImportError:
    TROCR_AVAILABLE = False
    print("⚠️  TrOCR not available. Install with: pip install transformers torch")

class TextExtractionService:
    def __init__(self):
        """Initialize the text extraction service"""
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']
        self.ocr_engines = []
        
        # Initialize available OCR engines
        if TESSERACT_AVAILABLE:
            self.ocr_engines.append('tesseract')
            print("🔍 Tesseract OCR engine loaded")
        
        if EASYOCR_AVAILABLE:
            self.ocr_engines.append('easyocr')
            print("🔍 EasyOCR engine loaded")
        
        if PADDLE_AVAILABLE:
            self.ocr_engines.append('paddleocr')
            print("🔍 PaddleOCR engine loaded")
        
        if TROCR_AVAILABLE:
            self.ocr_engines.append('trocr')
            print("🔍 TrOCR engine loaded")
        
        if not self.ocr_engines:
            print("❌ No OCR engines available. Please install at least one:")
            print("   pip install pytesseract easyocr transformers torch")
        
        # Initialize EasyOCR reader if available
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR reader initialized")
            except Exception as e:
                print(f"⚠️  EasyOCR reader failed to initialize: {e}")
        
        # Initialize PaddleOCR reader if available
        self.paddleocr_reader = None
        if PADDLE_AVAILABLE:
            try:
                # use_angle_cls improves rotated text handling; adjust as needed
                self.paddleocr_reader = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                print("✅ PaddleOCR reader initialized")
            except Exception as e:
                print(f"⚠️  PaddleOCR reader failed to initialize: {e}")

        # Initialize TrOCR if available
        self.trocr_processor = None
        self.trocr_model = None
        if TROCR_AVAILABLE:
            try:
                self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
                self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
                print("✅ TrOCR model loaded")
            except Exception as e:
                print(f"⚠️  TrOCR model failed to load: {e}")
        
        print(f"🚀 Text Extraction Service initialized with {len(self.ocr_engines)} OCR engines")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results (grayscale for Tesseract/EasyOCR)"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding for better text separation
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            print(f"⚠️  Image preprocessing failed: {e}")
            return image
    
    def preprocess_image_for_trocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image specifically for TrOCR (preserves RGB)"""
        try:
            # Ensure image is RGB (3 channels) for TrOCR
            if len(image.shape) == 2:
                # Convert grayscale to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3:
                if image.shape[2] == 3:
                    # Convert BGR to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                elif image.shape[2] == 4:
                    # Convert BGRA to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
                elif image.shape[2] == 1:
                    # Convert single channel to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Apply noise reduction while preserving RGB
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            
            # Apply slight contrast enhancement
            lab = cv2.cvtColor(denoised, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            return enhanced
            
        except Exception as e:
            print(f"⚠️  TrOCR image preprocessing failed: {e}")
            return image
    
    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect regions containing text in the image"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply MSER (Maximally Stable Extremal Regions) for text detection
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            # Filter regions by size and aspect ratio
            text_regions = []
            for region in regions:
                x, y, w, h = cv2.boundingRect(region)
                
                # Filter by size (too small or too large regions are likely not text)
                if 20 < w < 500 and 10 < h < 100:
                    # Filter by aspect ratio (text regions typically have specific ratios)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 10:
                        text_regions.append((x, y, w, h))
            
            # Merge overlapping regions
            merged_regions = self.merge_overlapping_regions(text_regions)
            
            return merged_regions
            
        except Exception as e:
            print(f"⚠️  Text region detection failed: {e}")
            return []
    
    def merge_overlapping_regions(self, regions: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Merge overlapping or nearby text regions"""
        if not regions:
            return []
        
        # Sort regions by x coordinate
        sorted_regions = sorted(regions, key=lambda x: x[0])
        merged = []
        current = list(sorted_regions[0])
        
        for region in sorted_regions[1:]:
            x, y, w, h = region
            
            # Check if regions overlap or are close
            if (x <= current[0] + current[2] + 20 and  # Close horizontally
                abs(y - current[1]) < 30):  # Close vertically
                
                # Merge regions
                current[0] = min(current[0], x)
                current[1] = min(current[1], y)
                current[2] = max(current[0] + current[2], x + w) - current[0]
                current[3] = max(current[1] + current[3], y + h) - current[1]
            else:
                merged.append(tuple(current))
                current = list(region)
        
        merged.append(tuple(current))
        return merged
    
    def extract_text_tesseract(self, image: np.ndarray, config: str = '--oem 3 --psm 6') -> str:
        """Extract text using Tesseract OCR"""
        try:
            if not TESSERACT_AVAILABLE:
                return "Tesseract not available"
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed, config=config)
            
            return text.strip()
            
        except Exception as e:
            print(f"❌ Tesseract OCR failed: {e}")
            return f"Tesseract error: {str(e)}"
    
    def extract_text_easyocr(self, image: np.ndarray) -> str:
        """Extract text using EasyOCR"""
        try:
            if not EASYOCR_AVAILABLE or self.easyocr_reader is None:
                return "EasyOCR not available"
            
            # Extract text with confidence threshold
            results = self.easyocr_reader.readtext(image, detail=0, paragraph=True)
            
            # Join results
            text = '\n'.join(results)
            return text.strip()
            
        except Exception as e:
            print(f"❌ EasyOCR failed: {e}")
            return f"EasyOCR error: {str(e)}"
    
    def extract_text_paddleocr(self, image: np.ndarray) -> str:
        """Extract text using PaddleOCR (CNN-based OCR pipeline)"""
        try:
            if not PADDLE_AVAILABLE or self.paddleocr_reader is None:
                return "PaddleOCR not available"
            # PaddleOCR expects RGB ndarray or path; ensure RGB
            if len(image.shape) == 2:
                rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = self.paddleocr_reader.ocr(rgb, cls=True)
            lines = []
            for page in result:
                for box, (txt, conf) in page:
                    # basic confidence filter
                    if conf is None or conf >= 0.5:
                        lines.append(txt)
            text = '\n'.join(lines)
            return text.strip()
        except Exception as e:
            print(f"❌ PaddleOCR failed: {e}")
            return f"PaddleOCR error: {str(e)}"

    def extract_text_trocr(self, image: np.ndarray) -> str:
        """Extract text using TrOCR (specialized for handwritten text)"""
        try:
            if not TROCR_AVAILABLE or self.trocr_processor is None or self.trocr_model is None:
                return "TrOCR not available"
            
            # Use TrOCR-specific preprocessing that preserves RGB
            processed_image = self.preprocess_image_for_trocr(image)
            
            # Convert to PIL format
            pil_image = Image.fromarray(processed_image)
            
            # Process image
            pixel_values = self.trocr_processor(pil_image, return_tensors="pt").pixel_values
            
            # Generate text
            with torch.no_grad():
                generated_ids = self.trocr_model.generate(pixel_values)
                generated_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return generated_text.strip()
            
        except Exception as e:
            print(f"❌ TrOCR failed: {e}")
            return f"TrOCR error: {str(e)}"
    
    def extract_text_from_image(self, image_path: str, engine: str = 'auto', 
                               preprocess: bool = True, detect_regions: bool = False) -> Dict[str, Any]:
        """Extract text from an image file"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"File not found: {image_path}",
                    "text": "",
                    "confidence": 0.0,
                    "regions": [],
                    "engine_used": "none"
                }
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": f"Failed to load image: {image_path}",
                    "text": "",
                    "confidence": 0.0,
                    "regions": [],
                    "engine_used": "none"
                }
            
            # Detect text regions if requested (use original image for detection)
            regions = []
            if detect_regions:
                regions = self.detect_text_regions(image)
            
            # Choose OCR engine
            if engine == 'auto':
                # Auto-select best engine based on image characteristics
                if TROCR_AVAILABLE and self._is_likely_handwritten(image):
                    engine = 'trocr'
                elif PADDLE_AVAILABLE:
                    engine = 'paddleocr'
                elif EASYOCR_AVAILABLE:
                    engine = 'easyocr'
                elif TESSERACT_AVAILABLE:
                    engine = 'tesseract'
                else:
                    engine = 'none'
            
            # Extract text using selected engine with appropriate preprocessing
            text = ""
            engine_used = engine
            
            if engine == 'tesseract':
                # Use grayscale preprocessing for Tesseract
                if preprocess:
                    processed_image = self.preprocess_image(image)
                else:
                    processed_image = image
                text = self.extract_text_tesseract(processed_image)
            elif engine == 'easyocr':
                # Use grayscale preprocessing for EasyOCR
                if preprocess:
                    processed_image = self.preprocess_image(image)
                else:
                    processed_image = image
                text = self.extract_text_easyocr(processed_image)
            elif engine == 'paddleocr':
                # Use grayscale preprocessing is not necessary; PaddleOCR works on RGB
                if preprocess:
                    processed_image = self.preprocess_image_for_trocr(image)
                else:
                    processed_image = image
                text = self.extract_text_paddleocr(processed_image)
            elif engine == 'trocr':
                # Use RGB preprocessing for TrOCR
                if preprocess:
                    processed_image = self.preprocess_image_for_trocr(image)
                else:
                    processed_image = image
                text = self.extract_text_trocr(processed_image)
            elif engine == 'all':
                # Try all engines and combine results with appropriate preprocessing
                results = {}
                if TESSERACT_AVAILABLE:
                    if preprocess:
                        processed_image = self.preprocess_image(image)
                    else:
                        processed_image = image
                    results['tesseract'] = self.extract_text_tesseract(processed_image)
                if EASYOCR_AVAILABLE:
                    if preprocess:
                        processed_image = self.preprocess_image(image)
                    else:
                        processed_image = image
                    results['easyocr'] = self.extract_text_easyocr(processed_image)
                if PADDLE_AVAILABLE:
                    if preprocess:
                        processed_image = self.preprocess_image_for_trocr(image)
                    else:
                        processed_image = image
                    results['paddleocr'] = self.extract_text_paddleocr(processed_image)
                if TROCR_AVAILABLE:
                    if preprocess:
                        processed_image = self.preprocess_image_for_trocr(image)
                    else:
                        processed_image = image
                    results['trocr'] = self.extract_text_trocr(processed_image)
                
                # Combine results (simple concatenation)
                text = "\n\n--- Tesseract ---\n" + results.get('tesseract', 'N/A')
                text += "\n\n--- EasyOCR ---\n" + results.get('easyocr', 'N/A')
                text += "\n\n--- PaddleOCR ---\n" + results.get('paddleocr', 'N/A')
                text += "\n\n--- TrOCR ---\n" + results.get('trocr', 'N/A')
                engine_used = 'combined'
            else:
                text = "No OCR engine available"
            
            # Calculate confidence (simple heuristic based on text length and content)
            confidence = self._calculate_confidence(text)
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "regions": regions,
                "engine_used": engine_used,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "regions": [],
                "engine_used": "none"
            }
    
    def extract_text_from_base64(self, base64_string: str, engine: str = 'auto',
                                preprocess: bool = True, detect_regions: bool = False) -> Dict[str, Any]:
        """Extract text from base64 encoded image"""
        try:
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "error": "Failed to decode base64 image",
                    "text": "",
                    "confidence": 0.0,
                    "regions": [],
                    "engine_used": "none"
                }
            
            # Detect text regions if requested (use original image for detection)
            regions = []
            if detect_regions:
                regions = self.detect_text_regions(image)
            
            # Choose OCR engine
            if engine == 'auto':
                if TROCR_AVAILABLE and self._is_likely_handwritten(image):
                    engine = 'trocr'
                elif EASYOCR_AVAILABLE:
                    engine = 'easyocr'
                elif TESSERACT_AVAILABLE:
                    engine = 'tesseract'
                else:
                    engine = 'none'
            
            # Extract text using selected engine with appropriate preprocessing
            text = ""
            engine_used = engine
            
            if engine == 'tesseract':
                # Use grayscale preprocessing for Tesseract
                if preprocess:
                    processed_image = self.preprocess_image(image)
                else:
                    processed_image = image
                text = self.extract_text_tesseract(processed_image)
            elif engine == 'easyocr':
                # Use grayscale preprocessing for EasyOCR
                if preprocess:
                    processed_image = self.preprocess_image(image)
                else:
                    processed_image = image
                text = self.extract_text_easyocr(processed_image)
            elif engine == 'trocr':
                # Use RGB preprocessing for TrOCR
                if preprocess:
                    processed_image = self.preprocess_image_for_trocr(image)
                else:
                    processed_image = image
                text = self.extract_text_trocr(processed_image)
            else:
                text = "No OCR engine available"
            
            confidence = self._calculate_confidence(text)
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "regions": regions,
                "engine_used": engine_used,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "regions": [],
                "engine_used": "none"
            }
    
    def _is_likely_handwritten(self, image: np.ndarray) -> bool:
        """Simple heuristic to detect if image likely contains handwritten text"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Handwritten text typically has more irregular edges
            return edge_density > 0.1
            
        except Exception:
            return False
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for extracted text"""
        if not text or text.strip() == "":
            return 0.0
        
        # Simple confidence calculation based on text characteristics
        confidence = 0.0
        
        # Length factor
        if len(text) > 100:
            confidence += 0.3
        elif len(text) > 50:
            confidence += 0.2
        elif len(text) > 10:
            confidence += 0.1
        
        # Content quality factors
        words = text.split()
        if len(words) > 5:
            confidence += 0.2
        
        # Check for common OCR artifacts
        if '|' in text or 'l' in text or 'I' in text:
            confidence += 0.1
        
        # Check for readable characters
        readable_chars = sum(1 for c in text if c.isalnum() or c.isspace())
        if len(text) > 0:
            readability = readable_chars / len(text)
            confidence += readability * 0.3
        
        return min(confidence, 1.0)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.supported_formats.copy()
    
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines"""
        return self.ocr_engines.copy()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and capabilities"""
        return {
            "service": "Text Extraction Service",
            "status": "active",
            "available_engines": self.ocr_engines,
            "supported_formats": self.supported_formats,
            "tesseract_available": TESSERACT_AVAILABLE,
            "easyocr_available": EASYOCR_AVAILABLE,
            "paddleocr_available": PADDLE_AVAILABLE,
            "trocr_available": TROCR_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }

# Create a global instance
text_extraction_service = TextExtractionService()

# Test function
def test_text_extraction():
    """Test the text extraction service"""
    print("🧪 Testing Text Extraction Service")
    print("=" * 50)
    
    # Test service status
    status = text_extraction_service.get_service_status()
    print(f"Service Status: {status['status']}")
    print(f"Available Engines: {status['available_engines']}")
    print(f"Supported Formats: {status['supported_formats']}")
    
    # Test with a sample image if available
    test_image = "sample_paper.jpg"  # You can create a test image
    if os.path.exists(test_image):
        print(f"\n🔍 Testing with {test_image}")
        result = text_extraction_service.extract_text_from_image(test_image, engine='auto')
        
        if result['success']:
            print(f"✅ Text extracted successfully!")
            print(f"   Engine used: {result['engine_used']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Text preview: {result['text'][:200]}...")
        else:
            print(f"❌ Text extraction failed: {result['error']}")
    else:
        print(f"\n📝 No test image found. Create {test_image} to test the service.")
        print("   You can test with any image containing text (printed or handwritten)")

if __name__ == "__main__":
    test_text_extraction()
