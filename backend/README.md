# Backend Setup

## System Dependencies

Before installing Python dependencies, ensure you have the following system dependencies installed:

### macOS
```bash
brew install tesseract espeak poppler llama.cpp
```

### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr espeak poppler-utils
```
For llama.cpp, use a prebuilt release from https://github.com/ggml-org/llama.cpp/releases or build it from source.

### Windows
Install the following:
- Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- eSpeak: http://espeak.sourceforge.net/download.html
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
- llama.cpp: https://github.com/ggml-org/llama.cpp/releases

## Python Dependencies

Install Python dependencies from the repo root:
```bash
pip install -r ../requirements.txt
```

## Environment Variables

Create a `.env` file in this directory with the following variables:
```env
LLM_BASE_URL=http://127.0.0.1:8080
LLM_API_KEY=
LLM_TIMEOUT=600
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

## Running the Application

```bash
python main.py
```

The backend will start on http://127.0.0.1:8000 by default.