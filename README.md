# MasterDocX

**A local-first AI document reader.** Upload a PDF, Word document or text file, then ask it questions,
get a summary, have passages explained, explore it as a mindmap or knowledge graph, and listen to the
answers. Everything runs on your own computer with a local LLM through [llama.cpp](https://github.com/ggml-org/llama.cpp),
so your documents never leave your machine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![llama.cpp](https://img.shields.io/badge/LLM-llama.cpp-black)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange)

---

## Features

- **Upload PDF, DOCX and TXT files.** Text is extracted automatically, with OCR (Tesseract) as a fallback for scanned PDFs.
- **Ask questions in plain language.** Answers are grounded in the most relevant passages of your document (retrieval-augmented generation).
- **Summaries.** One click summarizes the document; the summary is cached for next time.
- **Explain text.** Paste any passage and get it explained in simple terms.
- **Mindmap and knowledge graph.** The document's topics and the relationships between its entities, drawn as interactive graphs.
- **Text-to-speech.** Listen to answers, summaries and explanations (eSpeak).
- **Private by design.** No cloud APIs: the LLM, embeddings and vector database all run locally.
- **Bring your own model.** Use any GGUF chat model you already have (LM Studio, Ollama, Hugging Face...), or download one when you first start the app.

## How it works

```
                 ┌──────────────────────┐
  Browser  ───▶  │  React + Vite (5173) │
                 └──────────┬───────────┘
                            │ /api/v1
                 ┌──────────▼───────────┐      ┌──────────────────────────┐
                 │   FastAPI  (8000)    │ ───▶ │ llama.cpp llama-server   │
                 └──┬────────┬──────────┘      │ (8080, any GGUF model)   │
                    │        │                 └──────────────────────────┘
        ┌───────────▼──┐  ┌──▼──────────────────────────┐
        │ Text extract │  │ Embeddings (all-MiniLM-L6)  │
        │ PyPDF2, docx │  │ + ChromaDB vector store     │
        │ OCR fallback │  └─────────────────────────────┘
        └──────────────┘
```

1. **Ingest.** The uploaded file's text is extracted (OCR if a PDF has no text layer) and split into ~1,000-character chunks with 200 characters of overlap.
2. **Embed and store.** Each chunk is embedded with `all-MiniLM-L6-v2` (sentence-transformers) and stored in ChromaDB, one collection per document.
3. **Retrieve.** A question is embedded the same way and the 5 most similar chunks are retrieved.
4. **Generate.** The chunks and question go to the local LLM through llama-server's OpenAI-compatible API. Mindmap and graph requests use JSON mode so the output is always valid JSON.

## Quick start

### Requirements

| Needed for | Install (macOS) |
|---|---|
| Backend | Python 3.9+ |
| Frontend | Node.js 16+ (`brew install node`) |
| The LLM | llama.cpp (`brew install llama.cpp`) |
| Scanned PDFs (optional) | `brew install tesseract poppler` |
| Text-to-speech (optional) | `brew install espeak` |

On Linux, use your package manager (`tesseract-ocr`, `poppler-utils`, `espeak`) and a
[llama.cpp release](https://github.com/ggml-org/llama.cpp/releases). See [SETUP.md](SETUP.md) for Windows.

### Install and run

```bash
git clone https://github.com/AdityaGuhaa/MasterDocX.git
cd MasterDocX

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd frontend && npm install && cd ..

./start.sh
```

Then open **http://localhost:5173**, upload a document, and start asking questions.

### Choosing your LLM

The first time you run `./start.sh`, it asks whether you already have an LLM on your computer.
It never downloads anything without asking.

- **Yes:** it lists the GGUF models it finds (LM Studio, Ollama, llama.cpp and Hugging Face caches,
  `~/models`, `~/Downloads`) so you can pick one, or you can enter the path to any `.gguf` file.
- **No:** you can download Llama 3.1 8B Instruct (about 4.9 GB, recommended), Llama 3.2 3B Instruct
  (about 2.0 GB, for machines with less memory), any other GGUF model from Hugging Face, or skip it for now.

Your choice is remembered in `.llm-model`. Run `./start.sh --choose-model` to switch models.

Any instruction-tuned GGUF model works. Bigger models give better answers but need more memory;
a 7-8B model at Q4_K_M needs roughly 6-8 GB of RAM.

## Configuration

**Backend** settings go in `backend/.env` (all optional):

| Variable | Default | What it does |
|---|---|---|
| `LLM_BASE_URL` | `http://127.0.0.1:8080` | Address of llama-server |
| `LLM_API_KEY` | *(empty)* | Only if llama-server runs with `--api-key` |
| `LLM_TIMEOUT` | `600` | Seconds to wait for an LLM response |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model for embeddings |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1000` / `200` | Chunk size and overlap, in characters |
| `TOP_K_CHUNKS` | `5` | Chunks retrieved per question |
| `DATA_DIR` / `CHROMA_DB_DIR` | `./data` / `./data/chroma_db` | Where uploads, metadata and vectors are stored |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | Backend address |

**`start.sh`** reads these environment variables (all optional):

| Variable | What it does |
|---|---|
| `LLAMA_MODEL_PATH` | Use this `.gguf` file and skip the model question |
| `LLAMA_HF_MODEL` | Use (and download if needed) this Hugging Face model, e.g. `user/repo:Q4_K_M` |
| `LLAMA_PORT` | llama-server port (default `8080`) |
| `LLAMA_CTX` | Context size in tokens (default `8192`) |

## API

All endpoints are under `http://127.0.0.1:8000/api/v1`. Interactive docs are at `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload and process a document (multipart `file`) |
| `GET` | `/document/{doc_id}` | Document metadata |
| `POST` | `/query` | Ask a question: `{"doc_id", "query"}`; returns the answer and source chunks |
| `POST` | `/summarize` | Summarize: `{"doc_id", "force_regenerate"?}` |
| `POST` | `/explain` | Explain text: `{"doc_id", "text"}` |
| `POST` | `/tts` | Text to speech (WAV): `{"text"}` |
| `GET` | `/mindmap/{doc_id}` | Mindmap as nested JSON |
| `GET` | `/knowledge-graph/{doc_id}` | Knowledge graph as `nodes` and `edges` |

## Project structure

```
MasterDocX/
├── backend/
│   ├── main.py                 FastAPI app
│   ├── api/                    Routes and settings
│   ├── ingestion/              Text extraction and chunking
│   ├── embeddings/             sentence-transformers embedder
│   ├── storage/                ChromaDB vector store, JSON metadata store
│   ├── rag/                    Retriever
│   ├── llm/                    llama-server client and prompts
│   ├── ocr/                    Tesseract helpers
│   └── tts/                    eSpeak text-to-speech
├── frontend/
│   └── src/                    React app (upload page, document viewer)
├── scripts/
│   └── choose_model.py         Interactive LLM picker used by start.sh
├── start.sh                    Starts llama-server, backend and frontend
├── requirements.txt            Python dependencies
└── SETUP.md                    Detailed setup and troubleshooting
```

## Limitations

- Questions are answered from one document at a time.
- A document is identified by its file name, so uploading a different file with the same name replaces it.
- Summaries, mindmaps and graphs use the first ~10,000 characters of long documents.
- There's no authentication. It's meant to run on your own machine, not on a public server.

## Roadmap

- Docker setup
- Questions across multiple documents
- Show the source passages behind each answer in the UI
- Streaming responses
- Optional cloud LLM providers
- Automated tests

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you'd like to change.

## License

MasterDocX is released under the [MIT License](LICENSE).

Models you use with it have their own licenses. For example, Llama 3.x models are covered by Meta's Llama Community License.

## Author

**Aditya Guha** · [GitHub](https://github.com/AdityaGuhaa)
