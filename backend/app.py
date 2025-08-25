from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import time

# Import our services
from face_recognition_service import face_service, FaceRegisterRequest, FaceLoginRequest, FaceResponse
from chatbot_service_improved import chatbot_service
from text_extraction_service import text_extraction_service

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API with Face Recognition",
    description="A FastAPI-based RAG chatbot with document processing and face recognition capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug: Print environment variables
print(f"DEBUG: OLLAMA_BASE_URL = {os.getenv('OLLAMA_BASE_URL', 'NOT_SET')}")
print(f"DEBUG: OPENAI_MODEL = {os.getenv('OPENAI_MODEL', 'NOT_SET')}")
print(f"DEBUG: Current working directory = {os.getcwd()}")
print(f"DEBUG: .env file exists = {os.path.exists('.env')}")

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []
    settings: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, str]]
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    openai_configured: bool
    documents_loaded: int
    ollama_status: Optional[Dict[str, Any]] = None

# Chatbot API Endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with RAG capabilities"""
    try:
        # Get user message and settings
        user_message = request.message
        settings = request.settings or {}
        
        print(f"DEBUG: Received chat request - Message: {user_message[:100]}...")
        print(f"DEBUG: Settings: {settings}")
        
        # Use IMPROVED RAG method with conversation memory
        print(f"🚀 IMPROVED RAG: Using conversation memory and improved Ollama handling")
        response_data = chatbot_service.generate_rag_response_improved(
            user_message, 
            chat_history=request.chat_history,
            top_k=settings.get("top_k", 3),
            settings=settings,
            session_id="default"  # You can make this dynamic based on user session
        )
        
        print(f"DEBUG: Generated response with {len(response_data.get('sources', []))} sources")
        
        return ChatResponse(
            response=response_data["content"],
            sources=response_data["sources"],
            metadata=response_data["metadata"]
        )
        
    except Exception as e:
        print(f"ERROR: Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Get service stats
        chatbot_stats = chatbot_service.get_stats()
        face_stats = face_service.get_stats()
        
        # Test Ollama connection
        ollama_status = chatbot_service.test_ollama_connection()
        
        return HealthResponse(
            status="healthy" if ollama_status["status"] == "healthy" else "degraded",
            timestamp=time.time(),
            version="1.0.0",
            openai_configured=bool(os.getenv('OLLAMA_BASE_URL')),
            documents_loaded=chatbot_stats.get("documents_count", 0),
            ollama_status=ollama_status
        )
    except Exception as e:
        print(f"ERROR: Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Face Recognition API Endpoints
@app.post("/api/face/register", response_model=FaceResponse)
async def register_face(request: FaceRegisterRequest):
    """Register a new user with face recognition"""
    try:
        result = face_service.register_face(request.username, request.face_image)
        return result
    except Exception as e:
        print(f"ERROR: Face registration error: {e}")
        return FaceResponse(
            success=False,
            message=f"Registration failed: {str(e)}"
        )

@app.post("/api/face/login", response_model=FaceResponse)
async def login_with_face(request: FaceLoginRequest):
    """Login using face recognition"""
    try:
        result = face_service.login_with_face(request.face_image)
        return result
    except Exception as e:
        print(f"ERROR: Face login error: {e}")
        return FaceResponse(
            success=False,
            message=f"Login failed: {str(e)}"
        )

@app.get("/api/face/users")
async def get_registered_users():
    """Get list of registered users"""
    try:
        return face_service.get_registered_users()
    except Exception as e:
        print(f"ERROR: Get users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/face/stats")
async def get_face_recognition_stats():
    """Get face recognition service statistics"""
    try:
        return face_service.get_stats()
    except Exception as e:
        print(f"ERROR: Face stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chatbot/stats")
async def get_chatbot_stats():
    """Get chatbot service statistics"""
    try:
        return chatbot_service.get_stats()
    except Exception as e:
        print(f"ERROR: Chatbot stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chatbot/ollama-test")
async def test_ollama_connection():
    """Test connection to Ollama service"""
    try:
        return chatbot_service.test_ollama_connection()
    except Exception as e:
        print(f"ERROR: Ollama test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Text Extraction API Endpoints
class TextExtractionRequest(BaseModel):
    image_data: str  # Base64 encoded image
    engine: Optional[str] = "auto"
    preprocess: Optional[bool] = True
    detect_regions: Optional[bool] = False

@app.post("/api/extract-text")
async def extract_text_from_image(request: TextExtractionRequest):
    """Extract text from base64 encoded image"""
    try:
        print(f"🔄 Text extraction request received - Engine: {request.engine}")
        
        result = text_extraction_service.extract_text_from_base64(
            request.image_data,
            engine=request.engine,
            preprocess=request.preprocess,
            detect_regions=request.detect_regions
        )
        
        if result['success']:
            print(f"✅ Text extraction successful - Engine: {result['engine_used']}")
        else:
            print(f"❌ Text extraction failed: {result['error']}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: Text extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extract-text/engines")
async def get_available_engines():
    """Get available OCR engines"""
    try:
        engines = text_extraction_service.get_available_engines()
        return {"engines": engines}
    except Exception as e:
        print(f"ERROR: Get engines error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extract-text/status")
async def get_text_extraction_status():
    """Get text extraction service status"""
    try:
        return text_extraction_service.get_service_status()
    except Exception as e:
        print(f"ERROR: Text extraction status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    print("Initializing RAG Chatbot API with Face Recognition...")
    
    # Initialize chatbot service
    chatbot_service.initialize_sample_documents()
    
    print("API ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
