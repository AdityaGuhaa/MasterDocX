#!/bin/bash
# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

# Startup script for MasterDocX
# Starts the llama.cpp server (if needed), the backend and the frontend.
#
# LLM settings (override with environment variables):
#   LLAMA_MODEL_PATH  path to a local .gguf file (takes priority over LLAMA_HF_MODEL)
#   LLAMA_HF_MODEL    Hugging Face model to download/use (default: Llama 3.1 8B Instruct, Q4_K_M)
#   LLAMA_PORT        llama-server port (default: 8080)
#   LLAMA_CTX         context size in tokens (default: 8192)

echo "Starting MasterDocX..."

# Check if required commands are available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: Node.js/npm is not installed"
    exit 1
fi

LLAMA_PORT="${LLAMA_PORT:-8080}"
LLAMA_CTX="${LLAMA_CTX:-8192}"
LLAMA_HF_MODEL="${LLAMA_HF_MODEL:-bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:Q4_K_M}"
LLAMA_PID=""

# Point the backend at a non-default port unless LLM_BASE_URL is already set
if [ "$LLAMA_PORT" != "8080" ] && [ -z "$LLM_BASE_URL" ]; then
    export LLM_BASE_URL="http://127.0.0.1:${LLAMA_PORT}"
fi

# Start llama.cpp server unless one is already running
if curl -s -o /dev/null -m 2 "http://127.0.0.1:${LLAMA_PORT}/health"; then
    echo "llama.cpp server already running on port ${LLAMA_PORT}"
elif ! command -v llama-server &> /dev/null; then
    echo "Warning: llama-server (llama.cpp) is not installed. LLM features will not work."
    echo "         Install it with: brew install llama.cpp"
else
    if [ -n "$LLAMA_MODEL_PATH" ]; then
        MODEL_ARGS=(-m "$LLAMA_MODEL_PATH")
        echo "Starting llama.cpp server with $LLAMA_MODEL_PATH..."
    else
        MODEL_ARGS=(-hf "$LLAMA_HF_MODEL")
        echo "Starting llama.cpp server with $LLAMA_HF_MODEL..."
        echo "(The model is downloaded on first run, about 4.9 GB; see llama-server.log)"
    fi
    llama-server "${MODEL_ARGS[@]}" --host 127.0.0.1 --port "$LLAMA_PORT" -c "$LLAMA_CTX" \
        > llama-server.log 2>&1 &
    LLAMA_PID=$!
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
echo "LLM (llama.cpp): http://127.0.0.1:${LLAMA_PORT}"
echo ""
echo "Press Ctrl+C to stop all servers"

# Cleanup function
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    [ -n "$LLAMA_PID" ] && kill $LLAMA_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    [ -n "$LLAMA_PID" ] && wait $LLAMA_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
