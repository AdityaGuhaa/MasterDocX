from sentence_transformers import SentenceTransformer
import numpy as np
from api.settings import settings


class Embedder:
    def __init__(self):
        """Initialize the embedder with the specified model"""
        self.model = SentenceTransformer(settings.embedding_model)

    def generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []

        # Generate embeddings
        embeddings = self.model.encode(texts)

        # Convert to list of lists for JSON serialization
        return [embedding.tolist() for embedding in embeddings]

    def generate_embedding(self, text: str) -> list:
        """Generate embedding for a single text"""
        if not text:
            return []

        # Generate embedding
        embedding = self.model.encode([text])[0]

        # Convert to list for JSON serialization
        return embedding.tolist()