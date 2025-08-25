import os
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import json
import time
from datetime import datetime

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

class ChatbotService:
    def __init__(self):
        """Initialize the chatbot service with conversation memory"""
        self.documents = []
        self.document_embeddings = None
        self.document_metadata = []
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OPENAI_MODEL", "mistral:7b")
        
        # Conversation memory
        self.conversation_memory = {}
        self.user_info = {}
        
        # Load existing memory from file
        self.load_memory()
        
        print("Chatbot Service initialized with conversation memory")
    
    def load_memory(self):
        """Load conversation memory from file"""
        try:
            if os.path.exists('conversation_memory.json'):
                with open('conversation_memory.json', 'r') as f:
                    data = json.load(f)
                    self.conversation_memory = data.get('conversations', {})
                    self.user_info = data.get('user_info', {})
                print(f"Loaded memory: {len(self.conversation_memory)} conversations, {len(self.user_info)} users")
        except Exception as e:
            print(f"Could not load memory: {e}")
    
    def save_memory(self):
        """Save conversation memory to file"""
        try:
            data = {
                'conversations': self.conversation_memory,
                'user_info': self.user_info,
                'last_updated': datetime.now().isoformat()
            }
            with open('conversation_memory.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save memory: {e}")
    
    def extract_user_info(self, message: str) -> Dict[str, str]:
        """Extract user information from messages"""
        info = {}
        message_lower = message.lower()
        
        # Extract name
        name_patterns = [
            "my name is", "i'm", "i am", "call me", "this is"
        ]
        
        for pattern in name_patterns:
            if pattern in message_lower:
                # Find the name after the pattern
                start_idx = message_lower.find(pattern) + len(pattern)
                name_part = message[start_idx:].strip()
                # Take first word as name
                name = name_part.split()[0] if name_part.split() else ""
                if name and len(name) > 1:
                    info['name'] = name.title()
                    break
        
        # Extract age
        import re
        age_match = re.search(r'i am (\d+)', message_lower)
        if age_match:
            info['age'] = age_match.group(1)
        
        # Extract location
        location_patterns = ["i live in", "i'm from", "i am from"]
        for pattern in location_patterns:
            if pattern in message_lower:
                start_idx = message_lower.find(pattern) + len(pattern)
                location_part = message[start_idx:].strip()
                location = location_part.split()[0] if location_part.split() else ""
                if location and len(location) > 1:
                    info['location'] = location.title()
                    break
        
        return info
    
    def update_user_info(self, message: str, session_id: str = "default"):
        """Update user information from message"""
        extracted_info = self.extract_user_info(message)
        if extracted_info:
            if session_id not in self.user_info:
                self.user_info[session_id] = {}
            self.user_info[session_id].update(extracted_info)
            self.save_memory()
            print(f"Updated user info: {extracted_info}")
    
    def get_user_context(self, session_id: str = "default") -> str:
        """Get user context for responses"""
        if session_id not in self.user_info:
            return ""
        
        user = self.user_info[session_id]
        context_parts = []
        
        if 'name' in user:
            context_parts.append(f"User's name is {user['name']}")
        if 'age' in user:
            context_parts.append(f"User is {user['age']} years old")
        if 'location' in user:
            context_parts.append(f"User lives in {user['location']}")
        
        return ". ".join(context_parts) if context_parts else ""
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/embeddings",
                json={
                    "model": self.default_model,
                    "prompt": text
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Hash-based fallback
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            embedding = []
            for i in range(1536):
                byte_value = hash_bytes[i % len(hash_bytes)]
                embedding.append(float(byte_value) / 255.0)
            return embedding
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
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
        """Initialize with sample documents"""
        print("Processing documents and generating embeddings...")
        
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
            },
            {
                "content": "Gravity is a fundamental force of nature that attracts objects with mass toward each other. On Earth, gravity pulls everything toward the center of the planet, which is why objects fall when dropped.",
                "filename": "Gravity_Explanation.txt",
                "source": "sample_document"
            },
            {
                "content": "Power in physics refers to the rate at which work is done or energy is transferred. It is measured in watts (W) and represents how quickly energy is used or produced. Power can be calculated as work divided by time or force times velocity.",
                "filename": "Power_Physics.txt",
                "source": "sample_document"
            },
            {
                "content": "Electrical power is the rate at which electrical energy is transferred by an electric circuit. It is calculated as voltage times current (P = V × I) and is measured in watts. Higher power means more energy is being used per unit time.",
                "filename": "Electrical_Power.txt",
                "source": "sample_document"
            },
            {
                "content": "Computing power refers to the ability of a computer system to process data and perform calculations. It is often measured in terms of processing speed, memory capacity, and the ability to handle complex algorithms and large datasets.",
                "filename": "Computing_Power.txt",
                "source": "sample_document"
            }
        ]
        
        for doc in tqdm(sample_docs, desc="Generating embeddings"):
            content = doc["content"]
            chunks = self.chunk_text(content)
            
            for chunk in chunks:
                # Hash-based embeddings for consistency
                hash_obj = hashlib.md5(chunk.encode())
                hash_bytes = hash_obj.digest()
                embedding = []
                for i in range(1536):
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
            # Generate hash-based embedding for query
            hash_obj = hashlib.md5(query.encode())
            hash_bytes = hash_obj.digest()
            query_embedding = []
            for i in range(1536):
                byte_value = hash_bytes[i % len(hash_bytes)]
                query_embedding.append(float(byte_value) / 255.0)
            
            # Calculate similarity
            query_vector = np.array([query_embedding]).astype('float32')
            similarities = cosine_similarity(query_vector, self.document_embeddings)[0]
            
            # Get top-k most similar documents
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
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
    
    def call_ollama_with_retry(self, payload: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Call Ollama with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # More aggressive timeouts: 5s, 10s, 15s
                timeout = 5 + (attempt * 5)
                print(f"🔄 Ollama attempt {attempt + 1}/{max_retries} with {timeout}s timeout")
                
                # Optimize payload for faster response
                optimized_payload = payload.copy()
                if 'options' in optimized_payload:
                    optimized_payload['options']['num_predict'] = min(optimized_payload['options'].get('num_predict', 500), 100)
                    optimized_payload['options']['temperature'] = 0.7
                    optimized_payload['options']['top_p'] = 0.9
                
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=optimized_payload,
                    timeout=timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                print(f"⏰ Ollama timeout on attempt {attempt + 1} after {timeout}s")
                if attempt < max_retries - 1:
                    wait_time = 1  # Shorter wait between attempts
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                continue
                
            except Exception as e:
                print(f"❌ Ollama error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
        
        print(f"❌ All {max_retries} Ollama attempts failed")
        return None
    
    def generate_rag_response_improved(self, user_message: str, chat_history: List[Dict[str, Any]] = None, top_k: int = 3, settings: Dict[str, Any] = None, session_id: str = "default") -> Dict[str, Any]:
        """Generate RAG response with conversation memory and improved Ollama handling"""
        if settings is None:
            settings = {}
        
        if chat_history is None:
            chat_history = []
        
        try:
            print(f"🚀 IMPROVED RAG: Processing query: {user_message[:50]}...")
            
            # Update user info from message
            self.update_user_info(user_message, session_id)
            
            # Check for simple queries first
            simple_queries = [
                "hello", "hi", "how are you", "what's up", "thanks", "thank you",
                "bye", "goodbye", "help", "what can you do", "who are you"
            ]
            
            # Check for mathematical expressions
            import re
            math_pattern = re.compile(r'^[\d\s\+\-\*\/\(\)\.\^]+$')
            is_math = math_pattern.match(user_message.strip())
            
            # Check for simple greetings/questions
            is_simple = user_message.lower().strip() in simple_queries
            
            # Check for personal questions
            personal_patterns = [
                "what is my name", "what's my name", "who am i", "what do you know about me",
                "do you remember me", "what did i tell you"
            ]
            is_personal = any(pattern in user_message.lower() for pattern in personal_patterns)
            
            # Handle math queries
            if is_math:
                print(f"⚡ INSTANT MATH: {user_message}")
                try:
                    result = eval(user_message.strip())
                    return {
                        "content": f"**Calculation Result:** {user_message} = {result}\n\n**Step-by-step:**\n1. Expression: {user_message}\n2. Result: {result}",
                        "sources": [],
                        "metadata": {
                            "model": "instant_calculator",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "optimization": "instant_math"
                        }
                    }
                except:
                    return {
                        "content": f"I can see you want to calculate: {user_message}\n\nHowever, I'm having trouble processing this expression. Please try a simpler format like '6+9' or '10*5'.",
                        "sources": [],
                        "metadata": {
                            "model": "instant_calculator",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "optimization": "instant_math_fallback"
                        }
                    }
            
            # Handle personal questions
            if is_personal:
                print(f"👤 PERSONAL QUESTION: {user_message}")
                user_context = self.get_user_context(session_id)
                if user_context:
                    return {
                        "content": f"Based on our conversation, I know that {user_context}.\n\nIs there anything else you'd like me to remember about you?",
                        "sources": [],
                        "metadata": {
                            "model": "conversation_memory",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "optimization": "instant_personal"
                        }
                    }
                else:
                    return {
                        "content": "I don't have any specific information about you yet. You can tell me things like your name, age, or where you live, and I'll remember them for our conversation!",
                        "sources": [],
                        "metadata": {
                            "model": "conversation_memory",
                            "tokens_used": 0,
                            "rag_enabled": False,
                            "optimization": "instant_personal"
                        }
                    }
            
            # Handle simple greetings
            if is_simple:
                print(f"⚡ INSTANT GREETING: {user_message}")
                user_context = self.get_user_context(session_id)
                context_suffix = f" Nice to meet you, {user_context}!" if user_context else ""
                
                responses = {
                    "hello": f"Hello! 👋 How can I help you today?{context_suffix}",
                    "hi": f"Hi there! 😊 What would you like to know?{context_suffix}",
                    "how are you": "I'm doing great, thanks for asking! How can I assist you?",
                    "what's up": "Not much, just ready to help! What do you need?",
                    "thanks": "You're welcome! 😊",
                    "thank you": "You're very welcome! Is there anything else I can help with?",
                    "bye": "Goodbye! 👋 Have a great day!",
                    "goodbye": "See you later! 👋 Take care!",
                    "help": "I'm here to help! I can answer questions, perform calculations, and assist with various topics. What would you like to know?",
                    "what can you do": "I can help with:\n• Answering questions\n• Mathematical calculations\n• Remembering information about you\n• Providing information\n• General assistance\n\nWhat would you like help with?",
                    "who are you": "I'm your AI assistant! I'm here to help answer questions, perform calculations, and remember things about you. How can I assist you today?"
                }
                
                response = responses.get(user_message.lower().strip(), f"Hello! How can I help you today?{context_suffix}")
                return {
                    "content": response,
                    "sources": [],
                    "metadata": {
                        "model": "instant_response",
                        "tokens_used": 0,
                        "rag_enabled": False,
                        "optimization": "instant_greeting"
                    }
                }
            
            # For complex queries, use RAG with improved Ollama handling
            print(f"🔍 IMPROVED RAG: Complex query, searching documents...")
            
            # Search for relevant documents
            relevant_docs = self.search_similar_documents(user_message, top_k)
            
            # Prepare context
            context = ""
            sources = []
            
            if relevant_docs:
                for doc in relevant_docs:
                    content = doc["content"]
                    metadata = doc["metadata"]
                    context += content + "\n\n"
                    
                    source = {
                        "title": metadata.get("filename", "Document"),
                        "source": metadata.get("source", ""),
                        "snippet": content[:150] + "..." if len(content) > 150 else content,
                        "similarity_score": doc.get("similarity_score", "0")
                    }
                    sources.append(source)
                
                print(f"📚 Found {len(sources)} relevant documents")
            else:
                print("⚠️  No relevant documents found")
            
            # Add user context to the prompt
            user_context = self.get_user_context(session_id)
            user_context_prompt = f"\n\nUser Context: {user_context}" if user_context else ""
            
            # Create system prompt
            system_prompt = f"""You are a helpful AI assistant with access to a knowledge base and conversation memory. Use the following context to answer the user's question.

Context from knowledge base:
{context}

{user_context_prompt}

Answer the user's question based on the context provided. Be helpful, accurate, and conversational. If the context doesn't contain relevant information, say so politely and offer to help with other topics."""
            
            # Generate response using Ollama with retry logic
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
            
            print(f"🚀 IMPROVED RAG: Calling Ollama with retry logic...")
            response_data = self.call_ollama_with_retry(ollama_payload)
            
            if response_data:
                print(f"✅ Ollama response successful!")
                return {
                    "content": response_data["response"],
                    "sources": sources,
                    "metadata": {
                        "model": settings.get("model", self.default_model),
                        "tokens_used": response_data.get("eval_count", 0),
                        "rag_enabled": True,
                        "documents_retrieved": len(sources),
                        "optimization": "improved_rag_with_retry"
                    }
                }
            else:
                # Provide intelligent fallback based on available context
                print(f"⚠️  Ollama failed, providing intelligent fallback")
                
                if sources:
                    # Create a more intelligent fallback using the knowledge base
                    fallback_response = f"I understand you're asking about: **{user_message}**\n\n"
                    
                    # Group sources by topic and provide structured information
                    topics = {}
                    for source in sources:
                        title = source['title']
                        if title not in topics:
                            topics[title] = []
                        topics[title].append(source['snippet'])
                    
                    fallback_response += "Here's what I found in my knowledge base:\n\n"
                    
                    for i, (title, snippets) in enumerate(topics.items(), 1):
                        fallback_response += f"**{i}. {title}**\n"
                        # Combine snippets for this topic
                        combined_content = " ".join(snippets)
                        # Clean up and format the content
                        clean_content = combined_content.replace("...", "").strip()
                        if len(clean_content) > 200:
                            clean_content = clean_content[:200] + "..."
                        fallback_response += f"{clean_content}\n\n"
                    
                    # Add helpful context
                    if "artificial intelligence" in user_message.lower() or "ai" in user_message.lower():
                        fallback_response += "**AI Context**: I have information about artificial intelligence, machine learning, and natural language processing in my knowledge base.\n\n"
                    elif "gravity" in user_message.lower():
                        fallback_response += "**Physics Context**: I have information about gravity and fundamental forces in my knowledge base.\n\n"
                    elif "power" in user_message.lower():
                        fallback_response += "**Power Context**: I have comprehensive information about power in physics, electrical power, and computing power in my knowledge base.\n\n"
                    
                    fallback_response += "I'm experiencing some delays with the AI model right now, but I've provided the most relevant information from my knowledge base. Please try again in a moment for a more detailed AI-generated response."
                else:
                    # No sources found - provide helpful suggestions
                    fallback_response = f"I understand you're asking about: **{user_message}**\n\n"
                    
                    # Suggest related topics from our knowledge base
                    available_topics = [
                        "Artificial Intelligence (AI)",
                        "Machine Learning", 
                        "Natural Language Processing (NLP)",
                        "Gravity and Physics",
                        "Power (Physics, Electrical, Computing)"
                    ]
                    
                    fallback_response += f"I don't have specific information about this topic in my current knowledge base. However, I can help with:\n\n"
                    for topic in available_topics:
                        fallback_response += f"• **{topic}**\n"
                    
                    fallback_response += "\nI'm also experiencing delays with the AI model right now. Please try asking about one of the topics above, or try again later for a full response."
                
                return {
                    "content": fallback_response,
                    "sources": sources,
                    "metadata": {
                        "model": "fallback_response",
                        "tokens_used": 0,
                        "rag_enabled": True,
                        "documents_retrieved": len(sources),
                        "optimization": "intelligent_fallback_with_context"
                    }
                }
                
        except Exception as e:
            print(f"❌ IMPROVED RAG Error: {e}")
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot service statistics"""
        return {
            "documents_count": len(self.documents),
            "embeddings_loaded": self.document_embeddings is not None,
            "default_model": self.default_model,
            "ollama_base_url": self.ollama_base_url,
            "service_status": "active",
            "optimization": "improved_rag_with_memory",
            "conversations_stored": len(self.conversation_memory),
            "users_remembered": len(self.user_info)
        }
    
    def test_ollama_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama service"""
        try:
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
                timeout=10
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
