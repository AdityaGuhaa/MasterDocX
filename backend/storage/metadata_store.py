import json
import os
from pathlib import Path
from api.settings import settings
from typing import Dict, Any, Optional


class MetadataStore:
    def __init__(self):
        """Initialize metadata store"""
        self.metadata_file = os.path.join(settings.data_dir, "metadata.json")
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {str(e)}")

    def store_document_metadata(self, doc_id: str, metadata: Dict[str, Any]):
        """Store metadata for a document"""
        self.metadata[doc_id] = metadata
        self._save_metadata()

    def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a document"""
        return self.metadata.get(doc_id)

    def update_document_metadata(self, doc_id: str, updates: Dict[str, Any]):
        """Update metadata for a document"""
        if doc_id in self.metadata:
            self.metadata[doc_id].update(updates)
            self._save_metadata()

    def get_all_documents(self) -> Dict[str, Any]:
        """Get metadata for all documents"""
        return self.metadata

    def delete_document_metadata(self, doc_id: str):
        """Delete metadata for a document"""
        if doc_id in self.metadata:
            del self.metadata[doc_id]
            self._save_metadata()