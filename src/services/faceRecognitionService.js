import axios from 'axios';

// FaceRecognitionService - handles face recognition API calls
class FaceRecognitionService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Convert image file to base64
  async imageToBase64(file) {
    return new Promise((resolve, reject) => {
      try {
        // Handle both File objects and fallback objects
        if (file instanceof File) {
          // Standard File object
          const reader = new FileReader();
          reader.onload = () => {
            const base64 = reader.result.split(',')[1]; // Remove data:image/...;base64, prefix
            resolve(base64);
          };
          reader.onerror = reject;
          reader.readAsDataURL(file);
        } else if (file.arrayBuffer) {
          // Fallback object with arrayBuffer method
          file.arrayBuffer().then(buffer => {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
              binary += String.fromCharCode(bytes[i]);
            }
            const base64 = btoa(binary);
            resolve(base64);
          }).catch(reject);
        } else {
          reject(new Error('Unsupported file format'));
        }
      } catch (error) {
        reject(error);
      }
    });
  }

  // Register a new user with face recognition
  async registerFace(username, faceImage) {
    try {
      console.log('FaceRecognition: Registering face for user:', username);
      
      // Convert image to base64
      const base64Image = await this.imageToBase64(faceImage);
      
      const payload = {
        username: username,
        face_image: base64Image
      };

      console.log('FaceRecognition: Sending registration request');
      const response = await this.apiClient.post('/api/face/register', payload);
      
      console.log('FaceRecognition: Registration response:', response.data);
      return response.data;
      
    } catch (error) {
      console.error('FaceRecognition: Registration error:', error);
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.data?.message || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('Network error: Unable to connect to the server.');
      } else {
        throw new Error('An unexpected error occurred during registration.');
      }
    }
  }

  // Login using face recognition
  async loginWithFace(faceImage) {
    try {
      console.log('FaceRecognition: Attempting login with face');
      
      // Convert image to base64
      const base64Image = await this.imageToBase64(faceImage);
      
      const payload = {
        face_image: base64Image
      };

      console.log('FaceRecognition: Sending login request');
      const response = await this.apiClient.post('/api/face/login', payload);
      
      console.log('FaceRecognition: Login response:', response.data);
      return response.data;
      
    } catch (error) {
      console.error('FaceRecognition: Login error:', error);
      
      if (error.response) {
        throw new Error(`Server error: ${error.response.data?.message || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('Network error: Unable to connect to the server.');
      } else {
        throw new Error('An unexpected error occurred during login.');
      }
    }
  }

  // Get list of registered users
  async getRegisteredUsers() {
    try {
      const response = await this.apiClient.get('/api/face/users');
      return response.data;
    } catch (error) {
      console.error('FaceRecognition: Get users error:', error);
      throw new Error('Failed to fetch registered users.');
    }
  }

  // Test connection to the backend
  async testConnection() {
    try {
      const response = await this.apiClient.get('/api/health');
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('FaceRecognition: Health check error:', error);
      return false;
    }
  }
}

// Export singleton instance
export const faceRecognitionService = new FaceRecognitionService();
