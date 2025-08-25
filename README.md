# RAG Chatbot - React Frontend with FastAPI Backend

A modern chatbot application built with React frontend and FastAPI backend, featuring Retrieval-Augmented Generation (RAG) capabilities for intelligent, context-aware responses with document processing.

## 🚀 Features

- **Real-time Chat Interface**: Modern React-based chat UI with typing indicators
- **RAG Integration**: Retrieval-Augmented Generation for context-aware responses
- **Document Processing**: Upload and process PDF, DOCX, and text files
- **Vector Search**: FAISS-based similarity search for efficient document retrieval
- **Message History**: Persistent chat history with localStorage
- **Markdown Support**: Rich text rendering with syntax highlighting
- **Source Attribution**: Display sources for AI responses with similarity scores
- **Settings Panel**: Customize AI model parameters
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **Error Handling**: Comprehensive error handling and user feedback
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## 🛠 Technology Stack

### Frontend
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Markdown**: Markdown rendering
- **React Syntax Highlighter**: Code block highlighting
- **Axios**: HTTP client for API communication

### Backend
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Uvicorn**: High-performance ASGI server
- **Ollama**: Local LLM integration for AI model functionality
- **FAISS-CPU**: Facebook AI Similarity Search for efficient vector similarity search
- **PyPDF**: PDF text extraction
- **Python-docx**: Microsoft Word document text extraction
- **SQLAlchemy**: Database ORM for future persistence
- **Python-multipart**: File upload handling
- **TQDM**: Progress bars for long operations
- **NumPy**: Numerical computing for vector operations

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Ollama** (for local LLM functionality)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd chatbot
```

### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start
```

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env if needed (Ollama configuration is already set)
```

### 4. Configure Ollama

**Required: Ollama Installation and Setup**

1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Start Ollama service and pull a model (e.g., `ollama pull llama2`)
3. Copy `backend/env.example` to `backend/.env`
4. The `.env` file is already configured for Ollama with default settings

**📖 Detailed Setup Instructions**: See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for complete setup guide.

### 5. Start Development Servers

**Option 1: Manual Start**
```bash
# Terminal 1 - Frontend
npm start

# Terminal 2 - Backend
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Automated Scripts**
```bash
# Windows
start-dev.bat

# macOS/Linux
./start-dev.sh
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=e52b1597abcd422b80b41ab9647ebc6b.gUxpSlkeNlj8HEMl1WXzgJz5

# Optional: Customize AI settings
OPENAI_MODEL=llama2
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500

# Vector Database Configuration (ChromaDB)
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend Configuration

Update `src/services/chatService.js` to point to your backend:

```javascript
this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## 📁 Project Structure

```
chatbot/
├── public/                 # Static assets
├── src/                   # React source code
│   ├── components/        # React components
│   │   ├── Header.js     # Application header
│   │   ├── Sidebar.js    # Settings and history sidebar
│   │   ├── ChatInterface.js # Main chat component
│   │   ├── MessageList.js # Message rendering
│   │   ├── Message.js    # Individual message component
│   │   ├── MessageInput.js # User input component
│   │   └── TypingIndicator.js # Loading animation
│   ├── services/         # API services
│   │   └── chatService.js # Chat API communication
│   ├── App.js           # Main application component
│   └── index.js         # Application entry point
├── backend/              # FastAPI backend
│   ├── app.py           # Main FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── env.example      # Environment variables template
├── package.json          # Frontend dependencies
├── tailwind.config.js    # Tailwind CSS configuration
└── README.md            # This file
```

## 🎨 Customization

### Styling
- Modify `tailwind.config.js` for theme customization
- Update `src/index.css` for global styles
- Edit component-specific styles in `src/App.css`

### AI Models
- Change models in `backend/app.py` `get_models()` function
- Update model parameters in the settings panel
- Add new AI providers in the backend

### Document Processing
- Add new file types in `process_document()` function
- Customize text chunking in `chunk_text()` function
- Modify FAISS index configuration in `initialize_faiss()`

## 🚀 Deployment

### Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to your preferred platform:
# - Vercel: vercel --prod
# - Netlify: netlify deploy --prod
# - AWS S3: aws s3 sync build/ s3://your-bucket
```

### Backend Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn + Uvicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Deploy to:
# - Heroku: git push heroku main
# - Railway: railway up
# - DigitalOcean App Platform
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔮 Future Enhancements

- **WebSocket Support**: Real-time bidirectional communication
- **Advanced RAG**: Multi-modal retrieval, hybrid search
- **User Authentication**: User accounts and conversation management
- **Conversation Export**: Export chat history to various formats
- **Voice Input/Output**: Speech-to-text and text-to-speech
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Usage statistics and insights
- **Plugin System**: Extensible architecture for custom integrations
- **Database Integration**: SQLAlchemy for persistent storage
- **Advanced Vector Search**: HNSW, IVF indices for better performance

## 🐛 Troubleshooting

### Common Issues

1. **"react-scripts not found"**
   ```bash
   npm install
   npm start
   ```

2. **OpenAI API Errors**
   - Verify API key in `.env` file
   - Check API key permissions
   - Ensure sufficient credits

3. **Backend Connection Issues**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Ensure all dependencies are installed

4. **FAISS/Vector Search Issues**
   - Check NumPy version compatibility
   - Verify FAISS installation
   - Reset document index if needed

5. **Document Upload Issues**
   - Check file format support (PDF, DOCX, TXT)
   - Verify file size limits
   - Check temporary file permissions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Note**: This application requires an OpenAI API key for full functionality. The mock mode will work without an API key but provides limited responses.
