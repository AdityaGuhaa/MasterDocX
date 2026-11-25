# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

import hashlib
import logging
import chromadb
from chromadb.config import Settings
from api.settings import settings
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        """Initialize ChromaDB client"""
        # Create data directory if it doesn't exist
        chroma_path = os.path.abspath(settings.chroma_db_dir)
        Path(chroma_path).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

    @staticmethod
    def _collection_name(doc_id: str) -> str:
        """Map a doc_id (a file name) to a valid Chroma collection name.

        Chroma only allows 3-63 characters from [a-zA-Z0-9._-], so file names
        with spaces, brackets or long names can't be used directly. A hash of
        the doc_id is always valid and stays unique per file name.
        """
        return "doc_" + hashlib.sha256(doc_id.encode("utf-8")).hexdigest()[:32]

    def store_document_chunks(self, doc_id: str, chunks: list, embeddings: list):
        """Store document chunks and their embeddings"""
        # Create or get collection for this document
        collection_name = self._collection_name(doc_id)

        # Delete existing collection if it exists
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass  # Collection doesn't exist, that's fine

        # Create new collection
        collection = self.client.create_collection(collection_name)

        # Prepare data for insertion
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )

    def has_document(self, doc_id: str) -> bool:
        """Whether chunks for this document are stored"""
        try:
            return self.client.get_collection(self._collection_name(doc_id)).count() > 0
        except Exception:
            return False

    def retrieve_similar_chunks(self, doc_id: str, query_embedding: list, k: int = 5):
        """Retrieve k most similar chunks to the query"""
        collection_name = self._collection_name(doc_id)

        try:
            collection = self.client.get_collection(collection_name)

            # Query the collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, collection.count())
            )

            # Format results
            retrieved_chunks = []
            for i in range(len(results['ids'][0])):
                retrieved_chunks.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })

            return retrieved_chunks
        except Exception as e:
            logger.warning(f"Error retrieving chunks: {str(e)}")
            return []

    def get_all_chunks(self, doc_id: str):
        """Retrieve all chunks for a document"""
        collection_name = self._collection_name(doc_id)

        try:
            collection = self.client.get_collection(collection_name)

            # Get all documents
            results = collection.get()

            # Format results
            all_chunks = []
            for i in range(len(results['ids'])):
                all_chunks.append({
                    "id": results['ids'][i],
                    "text": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })

            # Chroma doesn't guarantee order, so restore document order
            all_chunks.sort(key=lambda chunk: chunk["metadata"].get("chunk_index", 0))

            return all_chunks
        except Exception as e:
            logger.warning(f"Error retrieving all chunks: {str(e)}")
            return []