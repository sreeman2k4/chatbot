import axios from 'axios';

// ChatService - handles all communication with the RAG backend API
// Manages message sending, response processing, and error handling
class ChatService {
  constructor() {
    // Base URL for the RAG API - update this to match your backend
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 120000, // 2 minute timeout (increased from 30 seconds)
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Send a message to the RAG backend and get response
  async sendMessage(message, chatHistory, settings) {
    try {
      console.log('Frontend: Sending message to backend...');
      
      // Prepare the request payload
      const payload = {
        message: message,
        chat_history: this.formatChatHistory(chatHistory),
        settings: {
          model: settings.model,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens,
          enable_rag: settings.enableRAG,
        },
      };

      console.log('Frontend: Request payload:', payload);

      // Make API request to RAG backend with timeout
      const response = await this.apiClient.post('/api/chat', payload);
      
      console.log('Frontend: Received response from backend:', response.data);
      
      return {
        content: response.data.response,
        sources: response.data.sources || [],
        metadata: response.data.metadata || {},
      };
    } catch (error) {
      console.error('Frontend: Chat API error:', error);
      
      // Handle different types of errors
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. The AI is taking longer than expected to respond. Please try again.');
      } else if (error.response) {
        // Server responded with error status
        throw new Error(`Server error: ${error.response.data?.message || error.response.statusText}`);
      } else if (error.request) {
        // Network error
        throw new Error('Network error: Unable to connect to the server. Please check your connection.');
      } else {
        // Other error
        throw new Error('An unexpected error occurred. Please try again.');
      }
    }
  }

  // Format chat history for API consumption
  formatChatHistory(chatHistory) {
    return chatHistory.map(message => ({
      role: message.type === 'user' ? 'user' : 'assistant',
      content: message.content,
      timestamp: message.timestamp,
    }));
  }

  // Upload documents for RAG knowledge base (future functionality)
  async uploadDocument(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.apiClient.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('Document upload error:', error);
      throw new Error('Failed to upload document. Please try again.');
    }
  }

  // Get available models from the backend
  async getAvailableModels() {
    try {
      const response = await this.apiClient.get('/api/models');
      return response.data.models;
    } catch (error) {
      console.error('Models API error:', error);
      // Return default models if API fails
      return [
        { id: 'phi:2.7b', name: 'Phi-2.7B (Ollama)' },
        { id: 'llama2:7b', name: 'Llama2-7B (Ollama)' },
        { id: 'mistral:7b', name: 'Mistral-7B (Ollama)' },
      ];
    }
  }

  // Test connection to the backend
  async testConnection() {
    try {
      const response = await this.apiClient.get('/api/health');
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Health check error:', error);
      return false;
    }
  }

  // Mock response for development/testing when backend is not available
  async getMockResponse(message) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    // Generate mock response based on message content
    const mockResponses = {
      hello: "Hello! I'm your AI assistant. How can I help you today?",
      help: "I can help you with various tasks including answering questions, providing explanations, and assisting with research. What would you like to know?",
      default: `I understand you said: "${message}". This is a mock response since the backend is not connected. In a real implementation, this would be processed by the RAG system to provide accurate, contextual responses based on the knowledge base.`
    };

    const lowerMessage = message.toLowerCase();
    let response = mockResponses.default;

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      response = mockResponses.hello;
    } else if (lowerMessage.includes('help')) {
      response = mockResponses.help;
    }

    return {
      content: response,
      sources: [
        {
          title: "Mock Source",
          url: "https://example.com",
          snippet: "This is a mock source for demonstration purposes."
        }
      ],
      metadata: {
        model: "mock-model",
        processing_time: Math.random() * 2 + 0.5,
        tokens_used: Math.floor(Math.random() * 100) + 50
      }
    };
  }
}

// Export singleton instance
export const chatService = new ChatService();






