#!/bin/bash

echo "Starting RAG Chatbot Development Environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed. Please install Python first."
    exit 1
fi

# Check if Ollama service is running
echo "Checking if Ollama service is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama service is running ✓"
else
    echo "Warning: Ollama service is not running on localhost:11434"
    echo "Please start Ollama service first:"
    echo "1. Install Ollama from https://ollama.ai"
    echo "2. Start Ollama service"
    echo "3. Pull a model: ollama pull llama2"
    echo ""
    read -p "Press Enter to continue anyway (backend may not work without Ollama)..."
fi

echo "Installing frontend dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "Error: Failed to install frontend dependencies."
    exit 1
fi

echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install backend dependencies."
    exit 1
fi

echo "Starting development servers..."

# Start frontend in a new terminal
gnome-terminal --title="Frontend Server" -- bash -c "cd $(pwd)/.. && npm start; exec bash"

# Start backend in a new terminal
gnome-terminal --title="Backend Server" -- bash -c "cd $(pwd) && uvicorn app:app --reload --host 0.0.0.0 --port 8000; exec bash"

echo ""
echo "Development servers are starting..."
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
wait
