@echo off
echo Starting RAG Chatbot Development Environment...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Check if Ollama service is running
echo Checking if Ollama service is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Warning: Ollama service is not running on localhost:11434
    echo Please start Ollama service first:
    echo 1. Install Ollama from https://ollama.ai
    echo 2. Start Ollama service
    echo 3. Pull a model: ollama pull llama2
    echo.
    echo Press any key to continue anyway (backend may not work without Ollama)...
    pause >nul
) else (
    echo Ollama service is running ✓
)

echo Installing frontend dependencies...
call npm install
if errorlevel 1 (
    echo Error: Failed to install frontend dependencies.
    pause
    exit /b 1
)

echo Installing backend dependencies...
cd backend
call pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install backend dependencies.
    pause
    exit /b 1
)

echo Starting development servers...

REM Start frontend in a new command prompt
start "Frontend Server" cmd /k "cd /d %CD% && npm start"

REM Start backend in a new command prompt
start "Backend Server" cmd /k "cd /d %CD%\backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Development servers are starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
