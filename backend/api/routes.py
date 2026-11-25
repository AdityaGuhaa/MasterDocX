# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import os
from pathlib import Path

from api.settings import settings
from embeddings.embedder import get_embedder
from ingestion.document_processor import DocumentProcessor, SUPPORTED_EXTENSIONS
from rag.retriever import Retriever
from llm.llm_interface import LLMInterface
from tts.tts_engine import TTSEngine
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore

router = APIRouter()

# Initialize components (the embedding model is loaded once and shared)
embedder = get_embedder()
vector_store = VectorStore()
metadata_store = MetadataStore()
document_processor = DocumentProcessor(vector_store, metadata_store, embedder)
retriever = Retriever(vector_store, embedder)
llm_interface = LLMInterface()
tts_engine = TTSEngine()

# Handlers other than /upload are plain `def` on purpose: they make blocking
# calls (embedding, Ollama, espeak), and FastAPI runs `def` handlers in a
# threadpool so one slow request doesn't freeze the whole server.


def _require_document(doc_id: str) -> dict:
    metadata = metadata_store.get_document_metadata(doc_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    return metadata


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    force_reprocess: Optional[bool] = Form(False)
):
    """Upload and process a document"""
    # Keep only the base name so a crafted filename (e.g. "../../x") can't
    # write outside the data directory.
    filename = Path(file.filename or "").name
    if not filename or filename in (".", ".."):
        raise HTTPException(status_code=400, detail="A file name is required")

    extension = os.path.splitext(filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {extension or 'none'}. "
                   f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    try:
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)

        file_path = os.path.join(settings.data_dir, filename)
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        result = await run_in_threadpool(
            document_processor.process_document,
            file_path,
            force_reprocess=force_reprocess
        )

        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{doc_id}")
def get_document_info(doc_id: str):
    """Get document information"""
    metadata = _require_document(doc_id)
    return JSONResponse(content=metadata)


@router.post("/query")
def query_document(query_request: dict):
    """Query document with RAG"""
    doc_id = query_request.get("doc_id")
    query = query_request.get("query")

    if not doc_id or not query:
        raise HTTPException(status_code=400, detail="doc_id and query are required")

    _require_document(doc_id)

    try:
        retrieved_chunks = retriever.retrieve(query, doc_id, k=settings.top_k_chunks)
        response = llm_interface.generate_response(query, retrieved_chunks)

        return JSONResponse(content={
            "query": query,
            "response": response,
            "sources": retrieved_chunks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
def summarize_document(summarize_request: dict):
    """Generate document summary"""
    doc_id = summarize_request.get("doc_id")

    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    metadata = _require_document(doc_id)

    # Return the cached summary unless a regeneration is requested
    existing_summary = metadata.get("summary")
    if existing_summary and not summarize_request.get("force_regenerate", False):
        return JSONResponse(content={"summary": existing_summary})

    try:
        all_chunks = retriever.retrieve_all(doc_id)
        summary = llm_interface.generate_summary(all_chunks)
        metadata_store.update_document_metadata(doc_id, {"summary": summary})

        return JSONResponse(content={"summary": summary})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
def explain_text(explain_request: dict):
    """Explain selected text"""
    doc_id = explain_request.get("doc_id")
    text = explain_request.get("text")

    if not doc_id or not text:
        raise HTTPException(status_code=400, detail="doc_id and text are required")

    _require_document(doc_id)

    try:
        explanation = llm_interface.generate_explanation(text)
        return JSONResponse(content={"explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts")
def text_to_speech(tts_request: dict):
    """Convert text to speech"""
    text = tts_request.get("text")

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    try:
        audio_stream = tts_engine.synthesize(text)
        return StreamingResponse(audio_stream, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mindmap/{doc_id}")
def get_mindmap(doc_id: str):
    """Get document mindmap structure"""
    _require_document(doc_id)

    try:
        all_chunks = retriever.retrieve_all(doc_id)
        mindmap = llm_interface.generate_mindmap(all_chunks)
        return JSONResponse(content={"mindmap": mindmap})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph/{doc_id}")
def get_knowledge_graph(doc_id: str):
    """Get document knowledge graph"""
    _require_document(doc_id)

    try:
        all_chunks = retriever.retrieve_all(doc_id)
        knowledge_graph = llm_interface.generate_knowledge_graph(all_chunks)
        return JSONResponse(content={"knowledge_graph": knowledge_graph})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
