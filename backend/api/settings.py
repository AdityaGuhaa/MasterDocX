from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API settings
    app_name: str = "AI Document Reader"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000

    # Storage settings
    data_dir: str = "./data"
    embeddings_dir: str = "./embeddings"
    chroma_db_dir: str = "./data/chroma_db"

    # Model settings
    embedding_model: str = "all-MiniLM-L6-v2"
    ollama_base_url: str = "http://localhost:11434"
    default_ollama_model: str = "mistral"

    # Processing settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_chunks: int = 5

    class Config:
        env_file = ".env"


settings = Settings()