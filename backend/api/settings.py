# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

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
    # llama.cpp server (llama-server) exposing its OpenAI-compatible API
    llm_base_url: str = "http://127.0.0.1:8080"
    llm_api_key: str = ""  # only needed if llama-server runs with --api-key
    llm_timeout: float = 600.0  # seconds; long documents can take a while on CPU

    # Processing settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_chunks: int = 5

    class Config:
        env_file = ".env"


settings = Settings()