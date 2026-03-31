# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered document reader application that processes PDF, DOCX, and TXT documents. It uses Retrieval-Augmented Generation (RAG) to enable intelligent querying of document content. The application consists of a Python/FastAPI backend and a React/Vite frontend.

### Key Features
- Document upload and processing (PDF, DOCX, TXT)
- Text extraction with OCR support for scanned documents
- Semantic chunking and embedding storage
- RAG-based question answering on document content
- Document summarization
- Text explanation feature
- Mindmap and knowledge graph generation
- Text-to-speech capabilities

## Architecture

### Backend (Python/FastAPI)
- **Main Entry Point**: `backend/main.py` - FastAPI application setup
- **API Routes**: `backend/api/routes.py` - REST endpoints for all features
- **Document Processing Pipeline**:
  - `backend/ingestion/document_processor.py` - Handles document ingestion, text extraction, and chunking
  - `backend/embeddings/embedder.py` - Generates embeddings using sentence-transformers
  - `backend/storage/vector_store.py` - Stores embeddings in ChromaDB
  - `backend/storage/metadata_store.py` - Manages document metadata in JSON format
- **Retrieval**: `backend/rag/retriever.py` - Retrieves relevant document chunks for queries
- **LLM Interface**: `backend/llm/llm_interface.py` - Communicates with Ollama for inference
- **TTS Engine**: `backend/tts/tts_engine.py` - Text-to-speech synthesis
- **OCR Engine**: `backend/ocr/ocr_engine.py` - Optical character recognition

### Frontend (React/Vite)
- **Entry Point**: `frontend/src/main.jsx`
- **Main Component**: `frontend/src/App.jsx`
- **Document Upload**: `frontend/src/pages/DocumentUploader.jsx`
- **Routing**: Uses react-router-dom for navigation

## Common Development Tasks

### Running the Application

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend will start on http://127.0.0.1:8000 by default.

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend will start on http://localhost:5173 by default.

### Testing

#### Backend Tests
Currently, there are no formal test files in the backend. Tests would typically be added in a `tests/` directory.

#### Frontend Tests
Currently, there are no formal test files in the frontend. Tests would typically be colocated with components using naming conventions like `Component.test.jsx`.

### Building for Production

#### Backend
No specific build process needed - Python files are executed directly.

#### Frontend
```bash
cd frontend
npm run build
```

Build output will be in `frontend/dist/`.

## Configuration

### Environment Variables
Create a `.env` file in the backend directory to override settings from `backend/api/settings.py`.

Key settings include:
- `OLLAMA_BASE_URL` - URL for Ollama service
- `DEFAULT_OLLA_MODEL` - Model name for Ollama
- `EMBEDDING_MODEL` - Model for sentence transformers
- `CHROMA_DB_DIR` - Directory for ChromaDB persistence

### Settings Management
All application settings are managed through `backend/api/settings.py` using pydantic-settings, which supports environment variables and `.env` files.

## Dependencies

### Backend
Key dependencies are listed in `backend/requirements.txt`:
- FastAPI - Web framework
- ChromaDB - Vector database
- Sentence Transformers - Embedding generation
- Ollama - Local LLM inference
- pdfminer.six, python-docx, Pillow, pytesseract - Document processing
- Piper TTS - Text-to-speech

### Frontend
Key dependencies are listed in `frontend/package.json`:
- React - UI framework
- React Router - Client-side routing
- Axios - HTTP client
- pdfjs-dist, react-pdf - PDF rendering
- vis-network - Visualization for mindmaps/graphs

## API Endpoints

Base URL: `/api/v1`

- POST `/upload` - Upload and process document
- GET `/document/{doc_id}` - Get document metadata
- POST `/query` - Query document with RAG
- POST `/summarize` - Generate document summary
- POST `/explain` - Explain selected text
- POST `/tts` - Convert text to speech
- GET `/mindmap/{doc_id}` - Get document mindmap
- GET `/knowledge-graph/{doc_id}` - Get document knowledge graph

## Data Flow

1. User uploads document via frontend
2. Frontend sends file to `/api/v1/upload` endpoint
3. DocumentProcessor extracts text (with OCR fallback)
4. Text is chunked and embedded using sentence-transformers
5. Embeddings stored in ChromaDB
6. Metadata stored in JSON file
7. User can query document via `/api/v1/query`
8. Retriever fetches relevant chunks from ChromaDB
9. LLM generates response using retrieved context

## Common Issues and Solutions

### Ollama Connection Issues
- Ensure Ollama service is running locally
- Verify `OLLAMA_BASE_URL` setting matches Ollama service URL
- Check that the specified model is pulled in Ollama

### PDF Processing Issues
- Scanned PDFs require OCR processing
- Large PDFs may need chunking optimization
- Password-protected PDFs are not supported

### ChromaDB Issues
- Database files stored in `./data/chroma_db` by default
- Clear the directory to reset vector storage
- Persistence issues may require checking directory permissions