# Setup and Testing Guide

This document provides instructions for setting up and testing the AI Document Reader application.

## Prerequisites

Before running the application, ensure you have the following installed:

1. Python 3.8+
2. Node.js 16+
3. Ollama (for LLM inference)
4. espeak (for text-to-speech, optional but recommended)

### Installing Ollama

Visit https://ollama.ai and follow installation instructions for your platform.

Pull a model for use with the application:
```bash
ollama pull llama3.1:8b
```

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

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
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

1. **Ollama connection errors**: Ensure Ollama is running and the model is pulled
2. **TTS not working**: Install espeak or check system audio settings
3. **PDF processing issues**: Ensure poppler-utils is installed for PDF processing
4. **CORS errors**: Make sure both backend and frontend are running

### Environment Variables

Create a `.env` file in the backend directory to override settings:

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_OLLA_MODEL=llama3.1:8b
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_DIR=./data/chroma_db
```

## Development Notes

### Project Structure

- `backend/` - Python/FastAPI backend
- `frontend/` - React/Vite frontend
- `CLAUDE.md` - Guidance for Claude Code
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