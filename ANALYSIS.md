## Repository Analysis

**Folder Overview**

- **`CLAUDE.md`** – Project-level documentation.
- **`backend/`** – Python server side, organized by responsibility:
  - `main.py` – entry point.
  - `api/` – FastAPI routes (`routes.py`) and settings.
  - `tts/tts_engine.py` – text-to-speech utilities.
  - `ocr/ocr_engine.py` – optical-character-recognition helper.
  - `rag/` – retrieval-augmented generation (`retriever.py`).
  - `storage/` – vector store (`vector_store.py`) and metadata store (`metadata_store.py`).
  - `embeddings/` – embedding generation (`embedder.py`).
  - `llm/` – language-model interface (`llm_interface.py`).
  - `ingestion/` – document processing pipeline (`document_processor.py`).
  - `utils/` – (currently empty) place for shared helpers.
  - `requirements.txt` – Python dependencies.
- **`frontend/`** – React front-end built with Vite:
  - `src/` – component hierarchy:
    - `App.jsx` / `App.css` – main UI shell.
    - `pages/DocumentUploader.jsx` – page for uploading docs.
    - `components/Header.jsx` – header component.
    - `index.css`, `main.jsx` – bootstrap.
  - `package.json` & `vite.config.js` – npm configuration.
- **`data/`**, **`embeddings/`**, **`models/`** – placeholder directories for runtime data, pre-computed embeddings, and model files (currently empty).

**Summary**

The repository hosts a full-stack “master-doc” application: a Python backend that handles OCR, TTS, embeddings, vector storage, and RAG-based LLM queries, exposed via API routes; and a React/Vite front-end for users to upload documents and interact with the service. Empty directories (`data`, `embeddings`, `models`) are ready for storing persisted assets.
