import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional, Dict, Any
from pydantic import BaseModel

# Pydantic models for face recognition
class FaceRegisterRequest(BaseModel):
    username: str
    face_image: str  # Base64 encoded image

class FaceLoginRequest(BaseModel):
    face_image: str  # Base64 encoded image

class FaceResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None

class FaceRecognitionService:
    def __init__(self):
        """Initialize the face recognition service"""
        self.face_encodings: Dict[str, np.ndarray] = {}  # Store face encodings for each user
        self.face_usernames: Dict[str, np.ndarray] = {}   # Store usernames for each face encoding
        
        # Load OpenCV's face detection cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        print("Face Recognition Service initialized")
    
    def encode_face_from_base64(self, base64_image: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Convert base64 image to face encoding using OpenCV"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to numpy array
            image_array = np.array(image)
            
            # Convert RGB to BGR (OpenCV format)
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please use an image with only one face."
            
            # Get the first (and only) face
            x, y, w, h = faces[0]
            
            # Extract face region and create a simple encoding
            face_region = gray[y:y+h, x:x+w]
            
            # Resize to standard size for consistency
            face_region = cv2.resize(face_region, (64, 64))
            
            # Create a simple feature vector (flattened and normalized)
            face_encoding = face_region.flatten().astype(np.float32) / 255.0
            
            return face_encoding, None
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def find_matching_face(self, face_encoding: np.ndarray, tolerance: float = 0.8) -> Optional[str]:
        """Find if a face encoding matches any stored faces using cosine similarity"""
        if not self.face_encodings:
            return None
        
        # Compare with all stored face encodings using cosine similarity
        for username, stored_encoding in self.face_encodings.items():
            # Calculate cosine similarity
            similarity = np.dot(face_encoding, stored_encoding) / (
                np.linalg.norm(face_encoding) * np.linalg.norm(stored_encoding)
            )
            
            if similarity > tolerance:
                return username
        
        return None
    
    def register_face(self, username: str, face_image: str) -> FaceResponse:
        """Register a new user with face recognition"""
        try:
            # Check if username already exists
            if username in self.face_encodings:
                return FaceResponse(
                    success=False,
                    message="Username already exists. Please choose a different username."
                )
            
            # Encode the face
            face_encoding, error = self.encode_face_from_base64(face_image)
            if error:
                return FaceResponse(success=False, message=error)
            
            # Store the face encoding
            self.face_encodings[username] = face_encoding
            self.face_usernames[username] = face_encoding
            
            return FaceResponse(
                success=True,
                message=f"Face registered successfully for user: {username}",
                username=username
            )
            
        except Exception as e:
            return FaceResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    def login_with_face(self, face_image: str) -> FaceResponse:
        """Login using face recognition"""
        try:
            # Encode the face
            face_encoding, error = self.encode_face_from_base64(face_image)
            if error:
                return FaceResponse(success=False, message=error)
            
            # Find matching face
            username = self.find_matching_face(face_encoding)
            if username:
                return FaceResponse(
                    success=True,
                    message=f"Login successful! Welcome back, {username}!",
                    username=username
                )
            else:
                return FaceResponse(
                    success=False,
                    message="Face not recognized. Please register first or try again."
                )
            
        except Exception as e:
            return FaceResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )
    
    def get_registered_users(self) -> Dict[str, Any]:
        """Get list of registered users"""
        return {
            "total_users": len(self.face_encodings),
            "users": list(self.face_encodings.keys())
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get face recognition service statistics"""
        return {
            "face_encodings_count": len(self.face_encodings),
            "face_usernames_count": len(self.face_usernames),
            "service_status": "active"
        }

# Create a global instance
face_service = FaceRecognitionService()

