# Text Extraction Service

A comprehensive OCR (Optical Character Recognition) service for extracting text from papers and documents, supporting both printed and handwritten text.

## 🚀 Features

- **Multiple OCR Engines**: Tesseract, EasyOCR, and TrOCR
- **Handwritten Text Support**: Specialized models for handwritten content
- **Image Preprocessing**: Automatic image enhancement for better OCR results
- **Text Region Detection**: Identify and locate text areas in images
- **Multiple Input Formats**: Support for image files and base64 encoded images
- **Confidence Scoring**: Quality assessment of extracted text
- **Auto-Engine Selection**: Intelligent choice of best OCR engine

## 📋 Requirements

### Python Dependencies
```bash
pip install -r requirements_text_extraction.txt
```

### System Dependencies

#### Windows
- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your PATH

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

## 🔧 Installation

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements_text_extraction.txt
   ```

2. **Install system dependencies** (see above)

3. **Test the installation:**
   ```bash
   python test_text_extraction.py
   ```

## 📖 Usage

### Basic Text Extraction

```python
from text_extraction_service import text_extraction_service

# Extract text from image file
result = text_extraction_service.extract_text_from_image(
    "paper.jpg",
    engine='auto',           # 'auto', 'tesseract', 'easyocr', 'trocr'
    preprocess=True,         # Enable image preprocessing
    detect_regions=True      # Detect text regions
)

if result['success']:
    print(f"Extracted text: {result['text']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Engine used: {result['engine_used']}")
else:
    print(f"Error: {result['error']}")
```

### Base64 Image Processing

```python
# Extract text from base64 encoded image
result = text_extraction_service.extract_text_from_base64(
    base64_string,
    engine='auto'
)
```

### Service Information

```python
# Get service status
status = text_extraction_service.get_service_status()
print(f"Available engines: {status['available_engines']}")
print(f"Supported formats: {status['supported_formats']}")

# Get available engines
engines = text_extraction_service.get_available_engines()
print(f"OCR engines: {engines}")
```

## 🧠 OCR Engines

### 1. Tesseract OCR
- **Best for**: Printed text, documents, books
- **Pros**: Fast, accurate for clean text, lightweight
- **Cons**: Limited handwritten text support

### 2. EasyOCR
- **Best for**: General text recognition, mixed content
- **Pros**: Good accuracy, supports many languages
- **Cons**: Slower than Tesseract

### 3. TrOCR (Transformer OCR)
- **Best for**: Handwritten text, cursive writing
- **Pros**: Excellent handwritten text recognition
- **Cons**: Larger model size, slower inference

## ⚙️ Configuration Options

### Engine Selection
- `'auto'`: Automatically choose best engine based on image content
- `'tesseract'`: Force Tesseract OCR
- `'easyocr'`: Force EasyOCR
- `'trocr'`: Force TrOCR (handwritten text)
- `'all'`: Try all engines and combine results

### Preprocessing Options
- `preprocess=True`: Enable automatic image enhancement
- `detect_regions=True`: Identify text regions in the image

## 📁 Supported Formats

- **Images**: JPG, JPEG, PNG, BMP, TIFF
- **Input Methods**: File paths, base64 strings
- **Output**: Structured JSON with text, confidence, and metadata

## 🔍 Text Region Detection

The service can identify where text is located in images:

```python
result = text_extraction_service.extract_text_from_image(
    "document.jpg",
    detect_regions=True
)

if result['success']:
    for i, (x, y, w, h) in enumerate(result['regions']):
        print(f"Text region {i+1}: Position ({x}, {y}), Size {w}x{h}")
```

## 📊 Confidence Scoring

The service provides confidence scores (0.0 to 1.0) based on:
- Text length and quality
- Character readability
- OCR engine reliability
- Image preprocessing success

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_text_extraction.py
```

This will:
1. Check service status and available engines
2. Create a sample test image (if OpenCV is available)
3. Test all OCR engines
4. Test base64 image processing
5. Demonstrate text region detection

## 🚨 Troubleshooting

### Common Issues

1. **"Tesseract not available"**
   - Install Tesseract system package
   - Ensure it's in your PATH

2. **"EasyOCR failed to initialize"**
   - Check internet connection (first run downloads models)
   - Verify PyTorch installation

3. **"TrOCR model failed to load"**
   - Check internet connection for model download
   - Verify transformers and torch versions

4. **Poor OCR results**
   - Enable preprocessing: `preprocess=True`
   - Try different engines
   - Check image quality and resolution

### Performance Tips

- **For printed text**: Use `engine='tesseract'`
- **For handwritten text**: Use `engine='trocr'`
- **For mixed content**: Use `engine='easyocr'`
- **For best results**: Use `engine='auto'`

## 🔗 Integration

The service can be easily integrated into your existing applications:

```python
# In your FastAPI app
@app.post("/extract-text")
async def extract_text(file: UploadFile):
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Extract text
    result = text_extraction_service.extract_text_from_image(temp_path)
    
    # Clean up
    os.remove(temp_path)
    
    return result
```

## 📝 License

This service is part of the chatbot project and follows the same licensing terms.

## 🤝 Contributing

To improve the text extraction service:
1. Test with different document types
2. Optimize preprocessing parameters
3. Add support for more OCR engines
4. Improve confidence scoring algorithms


