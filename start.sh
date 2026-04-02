#!/bin/bash

# Startup script for AI Document Reader
# This script starts both the backend and frontend servers

echo "Starting AI Document Reader..."

# Check if required commands are available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: Node.js/npm is not installed"
    exit 1
fi

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo "Warning: Ollama is not installed. LLM features will not work."
else
    # Check if llama3.1:8b model is available
    if ! ollama list | grep -q "llama3.1:8b"; then
        echo "Warning: Llama3.1:8b model not found. Pulling model..."
        ollama pull llama3.1:8b
    fi
fi

# Check if espeak is available for TTS
if ! command -v espeak &> /dev/null; then
    echo "Warning: espeak is not installed. TTS will use fallback audio."
fi

# Start backend in background
echo "Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Start frontend in background
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Servers started!"
echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID