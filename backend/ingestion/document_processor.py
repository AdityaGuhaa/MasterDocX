import os
import hashlib
from typing import Dict, Any
import PyPDF2
import docx
from PIL import Image
import pytesseract
from pathlib import Path

from storage.metadata_store import MetadataStore
from storage.vector_store import VectorStore
from embeddings.embedder import Embedder
from api.settings import settings


class DocumentProcessor:
    def __init__(self, vector_store: VectorStore, metadata_store: MetadataStore):
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.embedder = Embedder()

    async def process_document(self, file_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """Process a document through the full pipeline"""
        # Calculate file hash
        doc_hash = self._calculate_file_hash(file_path)
        doc_id = os.path.basename(file_path)

        # Check if document already processed
        existing_metadata = self.metadata_store.get_document_metadata(doc_id)

        if existing_metadata and not force_reprocess:
            # Check if file hash matches
            if existing_metadata.get("hash") == doc_hash:
                return {
                    "doc_id": doc_id,
                    "status": "already_processed",
                    "message": "Document already processed with same hash",
                    "metadata": existing_metadata
                }

        # Extract text from document
        text_content = self._extract_text(file_path)

        if not text_content.strip():
            return {
                "doc_id": doc_id,
                "status": "error",
                "message": "No text could be extracted from document"
            }

        # Split into chunks
        chunks = self._chunk_text(text_content)

        # Generate embeddings
        embeddings = self.embedder.generate_embeddings(chunks)

        # Store in vector database
        self.vector_store.store_document_chunks(doc_id, chunks, embeddings)

        # Store metadata
        metadata = {
            "doc_id": doc_id,
            "file_name": os.path.basename(file_path),
            "hash": doc_hash,
            "chunk_count": len(chunks),
            "character_count": len(text_content),
            "processed_at": self._get_current_timestamp()
        }

        self.metadata_store.store_document_metadata(doc_id, metadata)

        return {
            "doc_id": doc_id,
            "status": "success",
            "message": f"Document processed successfully with {len(chunks)} chunks",
            "metadata": metadata
        }

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            return self._extract_pdf_text(file_path)
        elif file_extension == ".docx":
            return self._extract_docx_text(file_path)
        elif file_extension == ".txt":
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF (including OCR for scanned PDFs)"""
        text = ""

        try:
            # Try to extract text normally first
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            # If no text extracted, try OCR
            if not text.strip():
                text = self._extract_pdf_ocr(file_path)

            return text
        except Exception as e:
            # Fallback to OCR
            return self._extract_pdf_ocr(file_path)

    def _extract_pdf_ocr(self, file_path: str) -> str:
        """Extract text from PDF using OCR"""
        try:
            from pdf2image import convert_from_path
            import pytesseract

            # Convert PDF to images
            images = convert_from_path(file_path)

            # Extract text from each image
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"

            return text
        except Exception as e:
            return f"OCR failed: {str(e)}"

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT: {str(e)}")

    def _chunk_text(self, text: str) -> list:
        """Split text into chunks for embedding"""
        # Simple chunking - in production, consider semantic chunking
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) > settings.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1  # +1 for space

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()