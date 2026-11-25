# Copyright (c) 2026 Aditya Guha
# SPDX-License-Identifier: MIT

import json
import logging
import re
import time
import httpx
from api.settings import settings
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Whole-document prompts (summary, mindmap, knowledge graph) get as much of the
# document as fits in llama-server's context window, which start.sh sizes to the
# machine's free memory. These leave room for the instructions and the answer.
PROMPT_RESERVE_TOKENS = 512
MAX_OUTPUT_TOKENS = 4096
# Used only if llama-server can't report its context size or count tokens
FALLBACK_DOCUMENT_CHARS = 10000
CONTEXT_CACHE_SECONDS = 60


class LLMInterface:
    def __init__(self):
        """Initialize LLM interface (talks to a llama.cpp llama-server)"""
        self.base_url = settings.llm_base_url.rstrip("/")
        headers = {}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=settings.llm_timeout,
        )
        self._context_size: Optional[int] = None
        self._context_checked_at = 0.0

    def context_size(self) -> Optional[int]:
        """Tokens available per request, as reported by llama-server (cached briefly)."""
        if time.monotonic() - self._context_checked_at < CONTEXT_CACHE_SECONDS:
            return self._context_size
        try:
            props = self.client.get("/props", timeout=5).json()
            n_ctx = int(props["default_generation_settings"]["n_ctx"])
            self._context_size = n_ctx if n_ctx > 0 else None
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            self._context_size = None
        self._context_checked_at = time.monotonic()
        return self._context_size

    def _output_tokens(self) -> int:
        n_ctx = self.context_size()
        return min(MAX_OUTPUT_TOKENS, n_ctx // 4) if n_ctx else MAX_OUTPUT_TOKENS

    def _count_tokens(self, text: str) -> int:
        response = self.client.post("/tokenize", json={"content": text}, timeout=60)
        response.raise_for_status()
        return len(response.json()["tokens"])

    def _fit_to_context(self, text: str) -> str:
        """Trim text so the whole prompt fits in llama-server's context window."""
        n_ctx = self.context_size()
        if not n_ctx:
            if len(text) > FALLBACK_DOCUMENT_CHARS:
                return text[:FALLBACK_DOCUMENT_CHARS] + "... (truncated)"
            return text

        budget = n_ctx - PROMPT_RESERVE_TOKENS - self._output_tokens()
        marker = "... (truncated)"
        try:
            trimmed = False
            for _ in range(3):
                tokens = self._count_tokens(text)
                if tokens <= budget:
                    break
                # Shrink proportionally, with a little slack, and re-check
                text = text[: int(len(text) * budget / tokens * 0.97)]
                trimmed = True
            return text + marker if trimmed else text
        except (httpx.HTTPError, KeyError, ValueError) as e:
            logger.warning(f"Couldn't count tokens ({e}); using a conservative estimate")
            max_chars = max(budget, 0) * 3  # roughly 3+ characters per token
            return text if len(text) <= max_chars else text[:max_chars] + "... (truncated)"

    def _generate(
        self,
        prompt: str,
        temperature: float,
        json_output: bool = False,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Send a chat request to llama-server's OpenAI-compatible API.

        Pass a single prompt, or a full list of chat messages for multi-turn
        conversations. The chat endpoint applies the model's own chat template,
        so instruct models get correctly formatted prompts.
        """
        payload = {
            "messages": messages or [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "top_p": 0.9,
            "max_tokens": self._output_tokens(),
        }
        if json_output:
            # llama-server turns this into a grammar, so the output is valid JSON
            payload["response_format"] = {"type": "json_object"}

        try:
            response = self.client.post("/v1/chat/completions", json=payload)
        except httpx.ConnectError:
            raise RuntimeError(
                f"Could not reach llama.cpp server at {self.base_url}. "
                "Is llama-server running? (see start.sh)"
            )
        if response.status_code == 503:
            raise RuntimeError("llama.cpp server is still loading the model; try again shortly")
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"].strip()

    def _document_text(self, chunks: List[Dict[str, Any]]) -> str:
        full_text = "\n\n".join([chunk["text"] for chunk in chunks])
        return self._fit_to_context(full_text)

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

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate response using RAG context.

        history: earlier turns of the conversation as chat messages
        ({"role": "user" | "assistant", "content": ...}), so follow-up
        questions like "why is that?" are understood.
        """
        # Format context from retrieved chunks
        context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])

        try:
            if not history:
                prompt = f"""Use the following context to answer the question according to the document.
If the context doesn't contain the information needed to answer the question, say so.

Context:
{context}

Question: {query}

Answer:"""
                return self._generate(prompt, temperature=0.7)

            messages = [
                {
                    "role": "system",
                    "content": "You answer questions about a document using the context passages provided "
                    "with each question. If the context doesn't contain the information needed, say so. "
                    "Use the earlier conversation to understand follow-up questions.",
                },
                *history,
                {
                    "role": "user",
                    "content": f"Context from the document:\n{context}\n\nQuestion: {query}",
                },
            ]
            return self._generate("", temperature=0.7, messages=messages)
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
