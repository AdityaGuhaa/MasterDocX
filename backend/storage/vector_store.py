import chromadb
from chromadb.config import Settings
import numpy as np
from api.settings import settings
from pathlib import Path
import os


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

    def store_document_chunks(self, doc_id: str, chunks: list, embeddings: list):
        """Store document chunks and their embeddings"""
        # Create or get collection for this document
        collection_name = f"doc_{doc_id.replace('.', '_').replace(' ', '_')}"

        # Delete existing collection if it exists
        try:
            self.client.delete_collection(collection_name)
        except:
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

    def retrieve_similar_chunks(self, doc_id: str, query_embedding: list, k: int = 5):
        """Retrieve k most similar chunks to the query"""
        collection_name = f"doc_{doc_id.replace('.', '_').replace(' ', '_')}"

        try:
            collection = self.client.get_collection(collection_name)

            # Query the collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k
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
            print(f"Error retrieving chunks: {str(e)}")
            return []

    def get_all_chunks(self, doc_id: str):
        """Retrieve all chunks for a document"""
        collection_name = f"doc_{doc_id.replace('.', '_').replace(' ', '_')}"

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

            return all_chunks
        except Exception as e:
            print(f"Error retrieving all chunks: {str(e)}")
            return []