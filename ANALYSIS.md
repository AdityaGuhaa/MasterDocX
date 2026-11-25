## Repository Analysis

**Folder Overview**

- **`backend/`** – Python server side, organized by responsibility:
  - `main.py` – entry point.
  - `api/` – FastAPI routes (`routes.py`) and settings.
  - `tts/tts_engine.py` – text-to-speech via the `espeak` CLI.
  - `ocr/ocr_engine.py` – optical-character-recognition helper.
  - `rag/` – retrieval-augmented generation (`retriever.py`).
  - `storage/` – vector store (`vector_store.py`) and metadata store (`metadata_store.py`).
  - `embeddings/` – embedding generation (`embedder.py`).
  - `llm/` – language-model interface (`llm_interface.py`).
  - `ingestion/` – document processing pipeline (`document_processor.py`).
  - `data/` – runtime data created on first run (uploads, `metadata.json`, `chroma_db/`); git-ignored.
- **`requirements.txt`** – Python dependencies (repo root, shared by backend).
- **`frontend/`** – React front-end built with Vite:
  - `src/` – component hierarchy:
    - `App.jsx` / `App.css` – main UI shell.
    - `pages/DocumentUploader.jsx` – page for uploading docs.
    - `pages/DocumentViewer.jsx` – document viewer with query, summary, explain, mindmap and TTS tools.
    - `components/Header.jsx` – header component.
    - `index.css`, `main.jsx` – bootstrap.
  - `package.json` & `vite.config.js` – npm configuration (dev server on port 5173).

**Summary**

The repository hosts a full-stack “master-doc” application: a Python backend that handles OCR, TTS, embeddings, vector storage, and RAG-based LLM queries, exposed via API routes; and a React/Vite front-end for users to upload documents and interact with the service. Runtime data (uploaded files, metadata and the ChromaDB store) lives under `backend/data/` and is not committed.
