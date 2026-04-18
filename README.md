# AI Document Reader

An intelligent document processing application that leverages Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to enable advanced querying, summarization, and analysis of PDF, DOCX, and TXT documents.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The AI Document Reader transforms static documents into interactive, intelligent knowledge bases. By combining document processing, semantic chunking, vector embeddings, and LLM-powered analysis, users can engage with their documents in entirely new ways:

- Ask natural language questions about document content
- Generate comprehensive summaries
- Extract explanations for specific text passages
- Visualize document structure through mindmaps and knowledge graphs
- Listen to documents through text-to-speech capabilities

This application bridges the gap between traditional document viewers and intelligent assistants, making information retrieval and comprehension more efficient and intuitive.

## Key Features

### 📚 Document Processing
- Support for PDF, DOCX, and TXT formats
- Automatic text extraction with OCR fallback for scanned documents
- Intelligent semantic chunking for optimal information retrieval

### 🔍 RAG-Powered Querying
- Natural language queries about document content
- Context-aware responses using retrieved relevant passages
- Source citation for transparency

### 📝 Smart Summarization
- Comprehensive document summaries
- Cached summaries for quick retrieval
- Regeneration capability for updated insights

### 💡 Text Explanation
- Detailed explanations of selected text passages
- Contextual understanding enhancement
- Educational support for complex content

### 🗺️ Visualization Tools
- Interactive mindmaps for document structure overview
- Knowledge graphs showing concept relationships
- Visual learning aids

### 🔊 Text-to-Speech
- Audio synthesis of document content
- Accessibility support for diverse user needs
- Multiple engine options (eSpeak, Piper TTS)

## Technology Stack

### Backend
| Component | Technology |
|----------|------------|
| Framework | FastAPI |
| Document Processing | pdfminer.six, python-docx, Pillow, pytesseract |
| Vector Storage | ChromaDB |
| Embeddings | sentence-transformers |
| LLM Interface | Ollama (llama3.1:8b) |
| TTS Engines | Piper TTS, eSpeak |
| OCR Engine | Tesseract |

### Frontend
| Component | Technology |
|----------|------------|
| Framework | React 18 |
| Build Tool | Vite |
| Routing | react-router-dom |
| HTTP Client | axios |
| PDF Rendering | pdfjs-dist, react-pdf |
| Visualization | vis-network |
| Styling | CSS Modules |

## Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Frontend      │    │    Backend       │
│   (React)       │◄──►│   (FastAPI)      │
└─────────────────┘    └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────┐      ┌──────────────┐     ┌──────────────┐
│ Document    │      │   RAG        │     │   LLM        │
│ Processing  │─────►│   Retrieval  │────►│   Interface  │
│ Pipeline    │      │              │     │              │
└─────────────┘      └──────────────┘     └──────────────┘
        │                     ▲                    ▲
        ▼                     │                    │
┌─────────────┐      ┌────────┴────────┐    ┌──────┴───────┐
│ Storage     │      │ Vector Storage  │    │ TTS Engine   │
│ (Metadata)  │      │ (ChromaDB)      │    │ (Piper/eSpeak)│
└─────────────┘      └─────────────────┘    └──────────────┘
```

### Core Components

1. **Document Processor**: Handles ingestion, text extraction, and semantic chunking
2. **Vector Store**: Stores document embeddings for similarity search
3. **Retriever**: Finds relevant document chunks for queries
4. **LLM Interface**: Communicates with Ollama for inference
5. **TTS Engine**: Converts text to speech
6. **Metadata Store**: Manages document metadata in JSON format

## Prerequisites

Before installing the application, ensure you have the following system dependencies:

### System Requirements
- Python 3.8+
- Node.js 16+
- npm 8+
- Ollama (for LLM features)

### System Dependencies

#### macOS
```bash
brew install tesseract espeak poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr espeak poppler-utils
```

#### Windows
Install the following:
- Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- eSpeak: http://espeak.sourceforge.net/download.html
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-document-reader
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Ollama Setup
Install Ollama from https://ollama.ai and pull the required model:
```bash
ollama pull llama3.1:8b
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_DIR=./data/chroma_db
DATA_DIR=./data
HOST=127.0.0.1
PORT=8000
DEBUG=True
APP_NAME="AI Document Reader"
CHUNK_SIZE=1000
TOP_K_CHUNKS=5
```

### Settings Management

All application settings are managed through `backend/api/settings.py` using pydantic-settings, which supports environment variables and `.env` files.

## Usage

### Starting the Application

#### Option 1: Using the Start Script (Recommended)
```bash
./start.sh
```

This script starts both backend and frontend servers and handles graceful shutdown.

#### Option 2: Manual Start

Start the backend:
```bash
cd backend
python main.py
```

Start the frontend:
```bash
cd frontend
npm run dev
```

### Accessing the Application

Once started, the application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000

## API Endpoints

Base URL: `/api/v1`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload and process document |
| `/document/{doc_id}` | GET | Get document metadata |
| `/query` | POST | Query document with RAG |
| `/summarize` | POST | Generate document summary |
| `/explain` | POST | Explain selected text |
| `/tts` | POST | Convert text to speech |
| `/mindmap/{doc_id}` | GET | Get document mindmap |
| `/knowledge-graph/{doc_id}` | GET | Get document knowledge graph |
| `/` | GET | Health check and welcome message |
| `/health` | GET | Application health status |

## Project Structure

```
ai-document-reader/
├── backend/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── settings.py        # Configuration management
│   ├── embeddings/
│   │   └── embedder.py        # Embedding generation
│   ├── ingestion/
│   │   └── document_processor.py # Document processing pipeline
│   ├── llm/
│   │   └── llm_interface.py   # LLM communication
│   ├── ocr/
│   │   └── ocr_engine.py      # OCR processing
│   ├── rag/
│   │   └── retriever.py       # Information retrieval
│   ├── storage/
│   │   ├── vector_store.py    # Vector database interface
│   │   └── metadata_store.py  # Document metadata management
│   ├── tts/
│   │   └── tts_engine.py      # Text-to-speech synthesis
│   ├── data/                  # Data storage directory
│   ├── main.py                # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Backend setup instructions
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── App.jsx            # Main application component
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Frontend dependencies
│   └── vite.config.js         # Build configuration
├── start.sh                   # Application startup script
└── README.md                  # This file
```

## Data Flow

1. **Document Upload**: User uploads document via frontend
2. **Processing**: Frontend sends file to `/api/v1/upload` endpoint
3. **Text Extraction**: DocumentProcessor extracts text (with OCR fallback)
4. **Chunking**: Text is semantically chunked for optimal retrieval
5. **Embedding**: Chunks are embedded using sentence-transformers
6. **Storage**: Embeddings stored in ChromaDB, metadata in JSON
7. **Querying**: User queries document via `/api/v1/query`
8. **Retrieval**: Retriever fetches relevant chunks from ChromaDB
9. **Generation**: LLM generates response using retrieved context

## Development

### Backend Development

#### Linting
```bash
cd backend
python -m flake8 .
```

#### Future Testing (when implemented)
```bash
cd backend
python -m pytest tests/
```

### Frontend Development

#### Linting
```bash
cd frontend
npm run lint
```

#### Future Testing (when implemented)
```bash
cd frontend
npm test
```

### Building for Production

#### Frontend Build
```bash
cd frontend
npm run build
```

Build output will be in `frontend/dist/`.

#### Backend Deployment
No specific build process needed - Python files are executed directly.

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama service is running locally
- Verify `OLLAMA_BASE_URL` setting matches Ollama service URL
- Check that the llama3.1:8b model is pulled in Ollama (`ollama pull llama3.1:8b`)

### PDF Processing Issues
- Scanned PDFs require OCR processing
- Large PDFs may need chunking optimization
- Password-protected PDFs are not supported

### ChromaDB Issues
- Database files stored in `./data/chroma_db` by default
- Clear the directory to reset vector storage
- Persistence issues may require checking directory permissions

### TTS Issues
- If eSpeak is not available, the application will use fallback audio
- Ensure eSpeak is properly installed and accessible in PATH

## Contributing

We welcome contributions to the AI Document Reader! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code follows our style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by Aditya Guha
</p>