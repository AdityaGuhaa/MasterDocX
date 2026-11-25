# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

import json
import re
import ollama
from api.settings import settings
from typing import List, Dict, Any

# llama3.1:8b runs with a small context window by default in Ollama, so cap how
# much document text goes into whole-document prompts.
MAX_DOCUMENT_CHARS = 10000


class LLMInterface:
    def __init__(self):
        """Initialize LLM interface"""
        self.base_url = settings.ollama_base_url
        self.model = settings.default_ollama_model
        # Use a client bound to the configured host; the module-level
        # ollama.generate() ignores OLLAMA_BASE_URL.
        self.client = ollama.Client(host=self.base_url)

    def _generate(self, prompt: str, temperature: float, json_output: bool = False) -> str:
        kwargs = {}
        if json_output:
            kwargs["format"] = "json"
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "top_p": 0.9,
            },
            **kwargs
        )
        return response["response"].strip()

    @staticmethod
    def _document_text(chunks: List[Dict[str, Any]]) -> str:
        full_text = "\n\n".join([chunk["text"] for chunk in chunks])
        if len(full_text) > MAX_DOCUMENT_CHARS:
            full_text = full_text[:MAX_DOCUMENT_CHARS] + "... (truncated)"
        return full_text

    @staticmethod
    def _parse_json(raw: str) -> Any:
        """Parse JSON from a model reply, tolerating code fences or extra prose."""
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start != -1 and end > start:
                return json.loads(cleaned[start:end + 1])
            raise

    def generate_response(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Generate response using RAG context"""
        # Format context from retrieved chunks
        context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])

        # Create prompt
        prompt = f"""Use the following context to answer the question according to the document.
If the context doesn't contain the information needed to answer the question, say so.

Context:
{context}

Question: {query}

Answer:"""

        try:
            return self._generate(prompt, temperature=0.7)
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_summary(self, chunks: List[Dict[str, Any]]) -> str:
        """Generate document summary"""
        full_text = self._document_text(chunks)

        prompt = f"""Summarize the following document content in a clear and concise manner.
Cover the main points and key information.

Content:
{full_text}

Summary:"""

        try:
            return self._generate(prompt, temperature=0.3)
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_explanation(self, text: str) -> str:
        """Generate explanation for selected text"""
        prompt = f"""Explain the following text in simple terms:

{text}

Explanation:"""

        try:
            return self._generate(prompt, temperature=0.5)
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def generate_mindmap(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mindmap structure from document.

        Raises an error (surfaced as a 500 by the API) when the model is
        unreachable or doesn't return a usable mindmap, instead of returning
        a made-up placeholder.
        """
        full_text = self._document_text(chunks)

        prompt = f"""Create a hierarchical mindmap structure representing the main topics and subtopics in the following document.
Return only a JSON object with a hierarchical structure.
Example format:
{{
  "title": "Main Topic",
  "children": [
    {{
      "title": "Subtopic 1",
      "children": [
        {{
          "title": "Detail 1"
        }}
      ]
    }}
  ]
}}

Document content:
{full_text}

Mindmap JSON:"""

        raw = self._generate(prompt, temperature=0.4, json_output=True)
        try:
            mindmap = self._parse_json(raw)
        except json.JSONDecodeError:
            raise ValueError("The model did not return valid mindmap JSON")

        if not isinstance(mindmap, dict) or "title" not in mindmap:
            raise ValueError("The model returned JSON that isn't a mindmap (missing 'title')")
        return mindmap

    def generate_knowledge_graph(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate knowledge graph from document.

        Raises an error (surfaced as a 500 by the API) when the model is
        unreachable or doesn't return a usable graph, instead of returning
        a made-up placeholder.
        """
        full_text = self._document_text(chunks)

        prompt = f"""Extract entities and relationships from the following document to create a knowledge graph.
Return only a JSON object with "nodes" and "edges" arrays.
Each node should have an "id" and "label".
Each edge should have "source", "target", and "label".

Example format:
{{
  "nodes": [
    {{"id": "1", "label": "Entity 1"}},
    {{"id": "2", "label": "Entity 2"}}
  ],
  "edges": [
    {{"source": "1", "target": "2", "label": "relationship"}}
  ]
}}

Document content:
{full_text}

Knowledge Graph JSON:"""

        raw = self._generate(prompt, temperature=0.4, json_output=True)
        try:
            knowledge_graph = self._parse_json(raw)
        except json.JSONDecodeError:
            raise ValueError("The model did not return valid knowledge graph JSON")

        if (
            not isinstance(knowledge_graph, dict)
            or not isinstance(knowledge_graph.get("nodes"), list)
            or not isinstance(knowledge_graph.get("edges"), list)
        ):
            raise ValueError("The model returned JSON that isn't a knowledge graph (needs 'nodes' and 'edges' lists)")
        return knowledge_graph
