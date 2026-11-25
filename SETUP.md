# Setup and Testing Guide

This document provides instructions for setting up and testing the AI Document Reader application.

## Prerequisites

Before running the application, ensure you have the following installed:

1. Python 3.8+
2. Node.js 16+
3. llama.cpp (for LLM inference)
4. espeak (for text-to-speech, optional but recommended)

### Installing llama.cpp

On macOS:
```bash
brew install llama.cpp
```

On other platforms, see https://github.com/ggml-org/llama.cpp for prebuilt binaries.

### Choosing a model

`start.sh` starts `llama-server` for you, but it never downloads a model on its own.
The first time you run it, it asks whether you already have an LLM on your computer:

- **Yes**: it lists the GGUF models it finds (LM Studio, Ollama, llama.cpp and Hugging Face
  caches, `~/models`, `~/Downloads`) so you can pick one, or you can type the path to any `.gguf` file.
- **No**: you can choose to download Llama 3.1 8B Instruct (about 4.9 GB, recommended),
  Llama 3.2 3B Instruct (about 2.0 GB, for machines with less memory), any other GGUF model from
  Hugging Face, or skip the LLM for now. A download starts only after you confirm it.

Your choice is saved in `.llm-model` (not committed) so you aren't asked again.
To pick a different model later:
```bash
./start.sh --choose-model
```

To skip the question, set `LLAMA_MODEL_PATH=/path/to/model.gguf` (or `LLAMA_HF_MODEL=user/repo:quant`).
To run llama.cpp yourself instead, start it before `start.sh` and it will be reused:
```bash
llama-server -m /path/to/model.gguf --port 8080 -np 1
```

### Context size

`start.sh` sizes the context window for your machine each time it starts (see `scripts/plan_context.py`):
it reads the free GPU memory from llama.cpp (on Apple Silicon, the unified memory macOS lets the GPU use;
without a GPU, free RAM), keeps 25% of it free, and lets llama.cpp work out the largest context that fits next
to the model, up to 64k tokens. It prints the result, for example:

```
Context: 65,536 tokens (capped at 65,536; 220,160 would fit). Memory: Apple M1 Pro: 14.0 GB free; keeping 3.5 GB free.
```

Set `LLAMA_CTX=16384` to use an exact size instead, or `LLAMA_CTX_MAX=131072` to raise the cap.
When you start `llama-server` yourself without `-c`, llama.cpp sizes the context automatically too.

### Installing espeak (for TTS)

On macOS:
```bash
brew install espeak
```

On Ubuntu/Debian:
```bash
sudo apt-get install espeak
```

On Windows:
Download and install eSpeak from http://espeak.sourceforge.net/

## Backend Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies (from the repo root):
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
python main.py
```

The backend will start on http://127.0.0.1:8000

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on http://localhost:5173

## Testing the Application

1. With both backend and frontend running, open your browser to http://localhost:5173

2. Upload a document (PDF, DOCX, or TXT) using the upload interface

3. After processing, you'll be redirected to the document viewer

4. Test the various features:
   - Query the document by asking questions
   - Generate a summary
   - Explain selected text
   - Generate mindmap and knowledge graph visualizations
   - Use text-to-speech on any text

## API Endpoints

You can also test the API directly:

- POST /api/v1/upload - Upload a document
- GET /api/v1/document/{doc_id} - Get document metadata
- POST /api/v1/query - Query document content
- POST /api/v1/summarize - Generate document summary
- POST /api/v1/explain - Explain text
- POST /api/v1/tts - Convert text to speech
- GET /api/v1/mindmap/{doc_id} - Get mindmap structure
- GET /api/v1/knowledge-graph/{doc_id} - Get knowledge graph

## Troubleshooting

### Common Issues

1. **LLM connection errors**: Ensure `llama-server` is running on port 8080 (check `llama-server.log` when started by `start.sh`) and has finished loading the model. If you skipped choosing a model, run `./start.sh --choose-model`
2. **TTS not working**: Install espeak or check system audio settings
3. **PDF processing issues**: Ensure poppler-utils and Tesseract are installed (needed for OCR on scanned PDFs)
4. **CORS errors**: Make sure both backend and frontend are running

### Environment Variables

Create a `.env` file in the backend directory to override settings:

```env
LLM_BASE_URL=http://127.0.0.1:8080
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_DIR=./data/chroma_db
```

## Development Notes

### Project Structure

- `backend/` - Python/FastAPI backend
- `frontend/` - React/Vite frontend
- `SETUP.md` - This setup guide

### Key Features Implemented

1. Document upload and processing
2. Text extraction with OCR support
3. Semantic search with RAG
4. Document summarization
5. Text explanation
6. Mindmap generation
7. Knowledge graph visualization
8. Text-to-speech