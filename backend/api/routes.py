from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import os
import hashlib
from pathlib import Path

from api.settings import settings
from ingestion.document_processor import DocumentProcessor
from rag.retriever import Retriever
from llm.llm_interface import LLMInterface
from tts.tts_engine import TTSEngine
from storage.vector_store import VectorStore
from storage.metadata_store import MetadataStore

router = APIRouter()

# Initialize components
vector_store = VectorStore()
metadata_store = MetadataStore()
document_processor = DocumentProcessor(vector_store, metadata_store)
retriever = Retriever(vector_store)
llm_interface = LLMInterface()
tts_engine = TTSEngine()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    force_reprocess: Optional[bool] = Form(False)
):
    """Upload and process a document"""
    try:
        # Create data directory if it doesn't exist
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)

        # Save file temporarily
        file_path = os.path.join(settings.data_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document
        result = await document_processor.process_document(
            file_path,
            force_reprocess=force_reprocess
        )

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document/{doc_id}")
async def get_document_info(doc_id: str):
    """Get document information"""
    try:
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(content=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_document(query_request: dict):
    """Query document with RAG"""
    try:
        doc_id = query_request.get("doc_id")
        query = query_request.get("query")

        if not doc_id or not query:
            raise HTTPException(status_code=400, detail="doc_id and query are required")

        # Check if document exists
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Retrieve relevant chunks
        retrieved_chunks = retriever.retrieve(query, doc_id, k=settings.top_k_chunks)

        # Generate response using LLM
        response = llm_interface.generate_response(query, retrieved_chunks)

        return JSONResponse(content={
            "query": query,
            "response": response,
            "sources": retrieved_chunks
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_document(summarize_request: dict):
    """Generate document summary"""
    try:
        doc_id = summarize_request.get("doc_id")

        if not doc_id:
            raise HTTPException(status_code=400, detail="doc_id is required")

        # Check if document exists
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check if summary already exists
        existing_summary = metadata.get("summary")
        if existing_summary and not summarize_request.get("force_regenerate", False):
            return JSONResponse(content={"summary": existing_summary})

        # Retrieve all chunks for comprehensive summary
        all_chunks = retriever.retrieve_all(doc_id)

        # Generate summary using LLM
        summary = llm_interface.generate_summary(all_chunks)

        # Update metadata with summary
        metadata_store.update_document_metadata(doc_id, {"summary": summary})

        return JSONResponse(content={"summary": summary})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_text(explain_request: dict):
    """Explain selected text"""
    try:
        doc_id = explain_request.get("doc_id")
        text = explain_request.get("text")

        if not doc_id or not text:
            raise HTTPException(status_code=400, detail="doc_id and text are required")

        # Check if document exists
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Generate explanation using LLM
        explanation = llm_interface.generate_explanation(text)

        return JSONResponse(content={"explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
async def text_to_speech(tts_request: dict):
    """Convert text to speech"""
    try:
        text = tts_request.get("text")
        doc_id = tts_request.get("doc_id")

        if not text:
            raise HTTPException(status_code=400, detail="text is required")

        # Generate speech
        audio_stream = tts_engine.synthesize(text)

        return StreamingResponse(audio_stream, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mindmap/{doc_id}")
async def get_mindmap(doc_id: str):
    """Get document mindmap structure"""
    try:
        # Check if document exists
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Retrieve all chunks for mindmap generation
        all_chunks = retriever.retrieve_all(doc_id)

        # Generate mindmap structure
        mindmap = llm_interface.generate_mindmap(all_chunks)

        return JSONResponse(content={"mindmap": mindmap})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-graph/{doc_id}")
async def get_knowledge_graph(doc_id: str):
    """Get document knowledge graph"""
    try:
        # Check if document exists
        metadata = metadata_store.get_document_metadata(doc_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Retrieve all chunks for knowledge graph generation
        all_chunks = retriever.retrieve_all(doc_id)

        # Generate knowledge graph
        knowledge_graph = llm_interface.generate_knowledge_graph(all_chunks)

        return JSONResponse(content={"knowledge_graph": knowledge_graph})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))