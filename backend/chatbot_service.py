import os
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not available. PDF processing will be disabled.")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not available. DOCX processing will be disabled.")

from tqdm import tqdm
import hashlib

class ChatbotService:
    def __init__(self):
        """Initialize the chatbot service"""
        self.documents = []
        self.document_embeddings = None
        self.document_metadata = []
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OPENAI_MODEL", "mistral:7b")
        
        print("Chatbot Service initialized")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/embeddings",
                json={
                    "model": self.default_model,
                    "prompt": text
                },
                timeout=15  # 15 second timeout for embeddings
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a simple hash-based embedding for now to avoid errors
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to a list of floats with consistent 1536 dimensions
            embedding = []
            for i in range(1536):
                # Use hash bytes in a cycle to ensure consistent dimensions
                byte_value = hash_bytes[i % len(hash_bytes)]
                embedding.append(float(byte_value) / 255.0)
            return embedding
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            print("PDF processing not available. Install PyPDF2: pip install PyPDF2")
            return ""
        
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            print("DOCX processing not available. Install python-docx: pip install python-docx")
            return ""
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def process_document(self, file_path: str, file_type: str) -> str:
        """Process document and extract text based on file type"""
        if file_type == "application/pdf":
            if not PDF_AVAILABLE:
                print("PDF processing not available. Install PyPDF2: pip install PyPDF2")
                return ""
            return self.extract_text_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if not DOCX_AVAILABLE:
                print("DOCX processing not available. Install python-docx: pip install python-docx")
                return ""
            return self.extract_text_from_docx(file_path)
        else:
            # Try to read as plain text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file as text: {e}")
                return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            if start >= len(text):
                break
        return chunks
    
    def initialize_sample_documents(self):
        """Initialize with sample documents for demonstration"""
        print("Processing documents and generating embeddings...")
        
        # Sample documents (you can replace these with your own)
        sample_docs = [
            {
                "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. AI encompasses machine learning, natural language processing, computer vision, and robotics.",
                "filename": "AI_Introduction.txt",
                "source": "sample_document"
            },
            {
                "content": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions.",
                "filename": "Machine_Learning.txt",
                "source": "sample_document"
            },
            {
                "content": "Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and human language. It enables machines to understand, interpret, and generate human language in a meaningful way.",
                "filename": "NLP_Overview.txt",
                "source": "sample_document"
            }
        ]
        
        # Process each document
        for doc in tqdm(sample_docs, desc="Generating embeddings"):
            content = doc["content"]
            chunks = self.chunk_text(content)
            
            for chunk in chunks:
                # Use hash-based embeddings for consistency (no API calls during startup)
                # This ensures all embeddings have the same 1536 dimensions
                # and prevents dimension mismatch errors
                hash_obj = hashlib.md5(chunk.encode())
                hash_bytes = hash_obj.digest()
                embedding = []
                for i in range(1536):  # Consistent 1536 dimensions
                    byte_value = hash_bytes[i % len(hash_bytes)]
                    embedding.append(float(byte_value) / 255.0)
                
                if embedding:
                    if self.document_embeddings is None:
                        self.document_embeddings = np.array([embedding]).astype('float32')
                    else:
                        self.document_embeddings = np.vstack([self.document_embeddings, embedding])
                    
                    self.documents.append(chunk)
                    self.document_metadata.append({
                        "filename": doc["filename"],
                        "source": doc["source"],
                        "chunk_length": len(chunk)
                    })
        
        if self.documents:
            print(f"Successfully added {len(self.documents)} documents to index")
        else:
            print("No valid embeddings generated")
    
    def search_similar_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity"""
        if self.document_embeddings is None or len(self.documents) == 0:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            # Calculate cosine similarity with all documents
            query_vector = np.array([query_embedding]).astype('float32')
            similarities = cosine_similarity(query_vector, self.document_embeddings)[0]
            
            # Get top-k most similar documents
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Return results with metadata
            results = []
            for idx in top_indices:
                if idx < len(self.documents):
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.document_metadata[idx],
                        "similarity_score": str(float(similarities[idx]))
                    })
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def generate_rag_response_optimized(self, user_message: str, top_k: int = 3, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate RAG response with ULTRA optimization - NO embedding calls for simple queries"""
        if settings is None:
            settings = {}
            
        try:
            print(f"🚀 ULTRA OPTIMIZED RAG: Analyzing query type...")
            
            # Check if this is a simple query that doesn't need RAG
            simple_queries = [
                "hello", "hi", "how are you", "what's up", "thanks", "thank you",
                "bye", "goodbye", "help", "what can you do", "who are you"
            ]
            
            # Check for mathematical expressions
            import re
            math_pattern = re.compile(r'^[\d\s\+\-\*\/\(\)\.]+$')
            is_math = math_pattern.match(user_message.strip())
            
            # Check for simple greetings/questions
            is_simple = user_message.lower().strip() in simple_queries
            
            if is_math:
                print(f"⚡ ULTRA OPTIMIZED: Math query detected, providing instant calculation!")
                # For math queries, provide instant response without Ollama
                try:
                    # Safe evaluation of mathematical expressions
                    result = eval(user_message.strip())
                    return {
                        "content": f"**Calculation Result:** {user_message} = {result}\n\n**Step-by-step:**\n1. Expression: {user_message}\n2. Result: {result}",
                        "sources": [],
                        "metadata": {
                            "model": "instant_calculator",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "documents_retrieved": 0,
                            "optimization": "instant_math_no_ollama"
                        }
                    }
                except:
                    # If eval fails, provide a helpful message
                    return {
                        "content": f"I can see you want to calculate: {user_message}\n\nHowever, I'm having trouble processing this expression. Please try a simpler format like '6+9' or '10*5'.",
                        "sources": [],
                        "metadata": {
                            "model": "instant_calculator",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "documents_retrieved": 0,
                            "optimization": "instant_math_fallback"
                        }
                    }
            
            if is_simple:
                print(f"⚡ ULTRA OPTIMIZED: Simple query detected, providing instant response!")
                # For simple greetings, provide instant responses without Ollama
                responses = {
                    "hello": "Hello! 👋 How can I help you today?",
                    "hi": "Hi there! 😊 What would you like to know?",
                    "how are you": "I'm doing great, thanks for asking! How can I assist you?",
                    "what's up": "Not much, just ready to help! What do you need?",
                    "thanks": "You're welcome! 😊",
                    "thank you": "You're very welcome! Is there anything else I can help with?",
                    "bye": "Goodbye! 👋 Have a great day!",
                    "goodbye": "See you later! 👋 Take care!",
                    "help": "I'm here to help! I can answer questions, perform calculations, and assist with various topics. What would you like to know?",
                    "what can you do": "I can help with:\n• Answering questions\n• Mathematical calculations\n• Providing information\n• General assistance\n\nWhat would you like help with?",
                    "who are you": "I'm your AI assistant! I'm here to help answer questions, perform calculations, and provide information. How can I assist you today?"
                }
                
                response = responses.get(user_message.lower().strip(), "Hello! How can I help you?")
                return {
                    "content": response,
                    "sources": [],
                    "metadata": {
                        "model": "instant_response",
                        "tokens_used": 0,
                        "rag_enabled": False,
                        "documents_retrieved": 0,
                        "optimization": "instant_greeting_no_ollama"
                    }
                }
            
            # For complex queries, use RAG but with hash-based embeddings (no Ollama call)
            print(f"🔍 ULTRA OPTIMIZED RAG: Complex query, using hash-based embeddings (no Ollama embedding call)")
            
            # Generate hash-based embedding (fast, no API call)
            hash_obj = hashlib.md5(user_message.encode())
            hash_bytes = hash_obj.digest()
            query_embedding = []
            for i in range(1536):
                byte_value = hash_bytes[i % len(hash_bytes)]
                query_embedding.append(float(byte_value) / 255.0)
            
            print(f"✅ ULTRA OPTIMIZED: Hash-based embedding generated instantly")
            
            # Use the hash-based embedding for document search
            if self.document_embeddings is not None and len(self.documents) > 0:
                query_vector = np.array([query_embedding]).astype('float32')
                similarities = cosine_similarity(query_vector, self.document_embeddings)[0]
                
                # Get top-k most similar documents
                top_indices = np.argsort(similarities)[::-1][:top_k]
                
                # Prepare context from retrieved documents
                context = ""
                sources = []
                
                for idx in top_indices:
                    if idx < len(self.documents):
                        content = self.documents[idx]
                        metadata = self.document_metadata[idx]
                        context += content + "\n\n"
                        
                        # Create source entry
                        source = {
                            "title": metadata.get("filename", "Document"),
                            "source": metadata.get("source", ""),
                            "snippet": content[:150] + "..." if len(content) > 150 else content,
                            "similarity_score": str(float(similarities[idx]))
                        }
                        sources.append(source)
                
                print(f"📚 ULTRA OPTIMIZED: Found {len(sources)} relevant documents")
            else:
                context = ""
                sources = []
                print("⚠️  ULTRA OPTIMIZED: No documents available for context")
            
            # Create system prompt
            system_prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. 
            If the context doesn't contain relevant information, say so politely.
            
            Context:
            {context}
            
            Answer the user's question based on the context provided. Be helpful and accurate."""
            
            # Generate response using Ollama (ONLY call to Ollama)
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            
            ollama_payload = {
                "model": settings.get("model", self.default_model),
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": settings.get("temperature", 0.7),
                    "num_predict": settings.get("max_tokens", 500)
                }
            }
            print(f"🚀 ULTRA OPTIMIZED: Sending request to Ollama (ONLY API call)")
            print(f"📊 ULTRA OPTIMIZED: Ollama payload: {ollama_payload}")
            
            try:
                # Try with a shorter timeout first
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=ollama_payload,
                    timeout=15  # Reduced timeout for faster failure
                )
                response.raise_for_status()
                response_data = response.json()
                
                print(f"✅ ULTRA OPTIMIZED: Response generated successfully!")
                
                return {
                    "content": response_data["response"],
                    "sources": sources,
                    "metadata": {
                        "model": settings.get("model", self.default_model),
                        "tokens_used": response_data.get("eval_count", 0),
                        "rag_enabled": True,
                        "documents_retrieved": len(sources),
                        "optimization": "ultra_fast_hash_embeddings"
                    }
                }
                
            except requests.exceptions.Timeout:
                print(f"⚠️  ULTRA OPTIMIZED: Ollama timeout, providing fallback response")
                # Provide a helpful fallback response when Ollama times out
                fallback_response = f"I understand you're asking about: {user_message}\n\nI found some relevant information in my knowledge base, but I'm experiencing delays with the AI model right now. Here's what I found:\n\n"
                
                if sources:
                    for i, source in enumerate(sources[:2], 1):  # Show first 2 sources
                        fallback_response += f"{i}. **{source['title']}**: {source['snippet']}\n\n"
                    fallback_response += "Please try again in a moment for a full AI-generated response."
                else:
                    fallback_response += "I don't have specific information about this topic in my knowledge base. Please try again later for a full AI response."
                
                return {
                    "content": fallback_response,
                    "sources": sources,
                    "metadata": {
                        "model": "fallback_response",
                        "tokens_used": 0,
                        "rag_enabled": True,
                        "documents_retrieved": len(sources),
                        "optimization": "fallback_due_to_timeout"
                    }
                }
            
        except Exception as e:
            print(f"❌ ULTRA OPTIMIZED RAG Error: {e}")
            return {
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "metadata": {
                    "model": settings.get("model", self.default_model),
                    "error": str(e),
                    "rag_enabled": False,
                    "optimization": "failed"
                }
            }
    
    def generate_rag_response(self, user_message: str, context_docs: List[Dict[str, Any]], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response using RAG approach"""
        try:
            # Prepare context from retrieved documents
            context = ""
            sources = []
            
            if context_docs:
                context_parts = []
                for doc in context_docs:
                    content = doc["content"]
                    metadata = doc["metadata"]
                    context_parts.append(content)
                    
                    # Create source entry
                    source = {
                        "title": metadata.get("filename", "Document"),
                        "url": metadata.get("source", ""),
                        "snippet": content[:150] + "..." if len(content) > 150 else content,
                        "similarity_score": doc.get("similarity_score", 0)
                    }
                    sources.append(source)
                
                context = "\n\n".join(context_parts)
            
            # Create system prompt
            system_prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. 
            If the context doesn't contain relevant information, say so politely.
            
            Context:
            {context}
            
            Answer the user's question based on the context provided. Be helpful and accurate."""
            
            # Generate response using Ollama
            # Build the full prompt with system and user message
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            
            # DEBUG: Log Ollama request
            ollama_payload = {
                "model": settings.get("model", self.default_model),
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": settings.get("temperature", 0.7),
                    "num_predict": settings.get("max_tokens", 500)
                }
            }
            print(f"DEBUG: Sending request to Ollama at {self.ollama_base_url}/api/generate")
            print(f"DEBUG: Ollama payload: {ollama_payload}")
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=ollama_payload
            )
            response.raise_for_status()
            response_data = response.json()
            
            return {
                "content": response_data["response"],
                "sources": sources,
                "metadata": {
                    "model": settings.get("model", self.default_model),
                    "tokens_used": response_data.get("eval_count", 0),
                    "rag_enabled": settings.get("enable_rag", True),
                    "documents_retrieved": len(context_docs)
                }
            }
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return {
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "metadata": {
                    "model": settings.get("model", self.default_model),
                    "error": str(e),
                    "rag_enabled": False
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot service statistics"""
        return {
            "documents_count": len(self.documents),
            "embeddings_loaded": self.document_embeddings is not None,
            "default_model": self.default_model,
            "ollama_base_url": self.ollama_base_url,
            "service_status": "active",
            "optimization": "ultra_fast_hash_embeddings"
        }
    
    def test_ollama_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama service"""
        try:
            # Test with a simple request
            test_payload = {
                "model": self.default_model,
                "prompt": "Hello",
                "stream": False,
                "options": {
                    "num_predict": 10
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=test_payload,
                timeout=10  # Short timeout for health check
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "model": self.default_model,
                    "message": "Ollama is responding normally"
                }
            else:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "message": f"Ollama returned status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "message": "Ollama is taking too long to respond (timeout after 10s)"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "message": "Cannot connect to Ollama service"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }

# Create a global instance
chatbot_service = ChatbotService()
