#!/bin/bash
# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

# Startup script for MasterDocX
# Starts the llama.cpp server (if needed), the backend and the frontend.
#
# On first run it asks which LLM to use: a model already on this computer, or
# a download (only after you confirm). The choice is saved in .llm-model.
#   ./start.sh --choose-model   pick a different model
#
# LLM settings (optional environment variables; these skip the question):
#   LLAMA_MODEL_PATH  path to a local .gguf file
#   LLAMA_HF_MODEL    Hugging Face model to download/use, e.g. user/repo:Q4_K_M
#   LLAMA_PORT        llama-server port (default: 8080)
#   LLAMA_CTX         context size in tokens (default: 8192)

cd "$(dirname "$0")" || exit 1

CHOOSE_MODEL=""
for arg in "$@"; do
    if [ "$arg" = "--choose-model" ]; then
        CHOOSE_MODEL="--reconfigure"
    fi
done

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
    MODEL_ARGS=()
    if [ -n "$LLAMA_MODEL_PATH" ]; then
        MODEL_ARGS=(-m "$LLAMA_MODEL_PATH")
    elif [ -n "$LLAMA_HF_MODEL" ]; then
        MODEL_ARGS=(-hf "$LLAMA_HF_MODEL")
    else
        # Ask the user (or use their saved choice); never downloads without a yes
        CHOICE="$(python3 scripts/choose_model.py --config .llm-model $CHOOSE_MODEL)"
        read -r KIND VALUE <<< "$CHOICE"
        case "$KIND" in
            m)  MODEL_ARGS=(-m "$VALUE") ;;
            hf) MODEL_ARGS=(-hf "$VALUE") ;;
        esac
    fi

    if [ ${#MODEL_ARGS[@]} -eq 0 ]; then
        echo "No LLM selected: starting without AI features (upload still works)."
        echo "         Run ./start.sh --choose-model to pick a model."
    else
        echo "Starting llama.cpp server with ${MODEL_ARGS[1]}..."
        if [ "${MODEL_ARGS[0]}" = "-hf" ]; then
            echo "(Downloads the model if it isn't cached yet; progress is in llama-server.log)"
        fi
        llama-server "${MODEL_ARGS[@]}" --host 127.0.0.1 --port "$LLAMA_PORT" -c "$LLAMA_CTX" \
            > llama-server.log 2>&1 &
        LLAMA_PID=$!
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
