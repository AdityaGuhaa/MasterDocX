from storage.vector_store import VectorStore
from embeddings.embedder import Embedder
from api.settings import settings


class Retriever:
    def __init__(self, vector_store: VectorStore):
        """Initialize retriever with vector store"""
        self.vector_store = vector_store
        self.embedder = Embedder()

    def retrieve(self, query: str, doc_id: str, k: int = None) -> list:
        """Retrieve relevant chunks for a query"""
        if k is None:
            k = settings.top_k_chunks

        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)

        # Retrieve similar chunks
        retrieved_chunks = self.vector_store.retrieve_similar_chunks(
            doc_id, query_embedding, k
        )

        return retrieved_chunks

    def retrieve_all(self, doc_id: str) -> list:
        """Retrieve all chunks for a document"""
        return self.vector_store.get_all_chunks(doc_id)