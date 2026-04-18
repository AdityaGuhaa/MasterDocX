# MasterDocX

A Local-First RAG-Based Knowledge System for Intelligent Document Understanding

---

## What is MasterDocX?

MasterDocX is a full-stack AI-powered document intelligence system that transforms static files into interactive, queryable knowledge bases.

It leverages Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to enable users to:

* Ask natural language questions about documents
* Generate summaries and explanations
* Visualize knowledge through mindmaps and graphs
* Convert text into speech

Unlike traditional document tools, MasterDocX is designed as a local-first AI system, ensuring privacy, control, and offline capability, while also being extensible to cloud-based LLMs.

---

## Problem Statement

Modern documents are:

* Static
* Hard to navigate
* Time-consuming to analyze

Users often struggle to:

* Extract key insights quickly
* Understand complex content
* Search contextually across large documents

---

## Solution

MasterDocX transforms documents into interactive AI-powered knowledge systems.

Using RAG, it:

1. Breaks documents into semantic chunks
2. Converts them into vector embeddings
3. Retrieves relevant context
4. Uses LLMs to generate intelligent responses

---

## Key Features

### Document Processing

* Supports PDF, DOCX, TXT
* OCR fallback for scanned documents
* Semantic chunking

### RAG-Based Querying

* Context-aware question answering
* Source-grounded responses

### Smart Summarization

* Full document summaries
* Regeneration support

### Text Explanation

* Explain selected passages
* Simplify complex content

### Visualization

* Mindmaps
* Knowledge graphs

### Text-to-Speech

* Convert content into audio
* Accessibility support

---

## Architecture Overview

```
User
  ↓
Frontend (React)
  ↓
Backend (FastAPI)
  ↓
Document Pipeline → Embeddings → Vector DB (ChromaDB)
  ↓
Retriever (Top-K chunks)
  ↓
LLM (Ollama / Future: Gemini, OpenAI)
  ↓
Response
```

---

## Data Flow

1. Upload document
2. Extract text (OCR if needed)
3. Chunk text semantically
4. Generate embeddings
5. Store in vector DB
6. Query → retrieve relevant chunks
7. LLM generates response

---

## Tech Stack

### Backend

* FastAPI
* ChromaDB
* sentence-transformers
* Ollama (local LLM)
* Tesseract OCR
* Piper TTS / eSpeak

### Frontend

* React + Vite
* Axios
* PDF.js
* vis-network (graphs)

---

## Core Philosophy

### Local-First AI

* Runs fully offline using local LLMs
* Ensures privacy and data control

### Hybrid Future

* Planned support for:

  * Google Gemini
  * OpenAI

---

## Target Users

* Students (learning and revision)
* Researchers (document analysis)
* Developers (knowledge extraction)
* General users (intelligent reading)

---

## Getting Started

### 1. Clone Repo

```
git clone https://github.com/AdityaGuhaa/MasterDocX.git
cd MasterDocX
```

### 2. Backend Setup

```
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```
cd frontend
npm install
```

### 4. Run App

```
./start.sh
```

---

## Configuration

Create `.env` inside backend:

```
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama3.1:8b
CHUNK_SIZE=1000
TOP_K_CHUNKS=5
```

---

## Project Structure

```
backend/
  api/
  embeddings/
  ingestion/
  rag/
  storage/
  llm/
  tts/
frontend/
  src/
start.sh
```

---

## Why MasterDocX?

Compared to tools like ChatGPT or NotebookLM:

* Works offline (local-first)
* Full control over data
* Customizable pipeline
* Visual knowledge tools

---

## Roadmap

* Docker support
* Cloud LLM integration (Gemini/OpenAI)
* Multi-document querying
* Persistent knowledge graphs
* User authentication

---

## Contributing

Pull requests are welcome.

---

## License

MIT License

---

## Author

Aditya Guha

---

Turning documents into intelligence.
