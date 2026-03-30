import json
import ollama
from api.settings import settings
from typing import List, Dict, Any


class LLMInterface:
    def __init__(self):
        """Initialize LLM interface"""
        self.base_url = settings.ollama_base_url
        self.model = settings.default_ollama_model

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

        # Generate response using Ollama
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_summary(self, chunks: List[Dict[str, Any]]) -> str:
        """Generate document summary"""
        # Combine chunks for summary
        full_text = "\n\n".join([chunk["text"] for chunk in chunks])

        # Truncate if too long for summary
        max_chars = 10000
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "... (truncated for summary)"

        prompt = f"""Summarize the following document content in a clear and concise manner.
Cover the main points and key information.

Content:
{full_text}

Summary:"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                }
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_explanation(self, text: str) -> str:
        """Generate explanation for selected text"""
        prompt = f"""Explain the following text in simple terms:

{text}

Explanation:"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.5,
                    "top_p": 0.9,
                }
            )
            return response["response"].strip()
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def generate_mindmap(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mindmap structure from document"""
        full_text = "\n\n".join([chunk["text"] for chunk in chunks])

        prompt = f"""Create a hierarchical mindmap structure representing the main topics and subtopics in the following document.
Return the result as a JSON object with a hierarchical structure.
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

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.4,
                    "top_p": 0.9,
                }
            )

            # Try to parse JSON response
            try:
                mindmap = json.loads(response["response"].strip())
                return mindmap
            except:
                # If parsing fails, return a simple structure
                return {
                    "title": "Document Mindmap",
                    "children": [
                        {
                            "title": "Main Topics",
                            "children": [
                                {"title": "Key Points"},
                                {"title": "Important Details"}
                            ]
                        }
                    ]
                }
        except Exception as e:
            return {
                "title": "Document Mindmap",
                "children": [
                    {
                        "title": "Main Topics",
                        "children": [
                            {"title": "Key Points"},
                            {"title": "Important Details"}
                        ]
                    }
                ]
            }

    def generate_knowledge_graph(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate knowledge graph from document"""
        full_text = "\n\n".join([chunk["text"] for chunk in chunks])

        prompt = f"""Extract entities and relationships from the following document to create a knowledge graph.
Return the result as a JSON object with "nodes" and "edges" arrays.
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

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.4,
                    "top_p": 0.9,
                }
            )

            # Try to parse JSON response
            try:
                knowledge_graph = json.loads(response["response"].strip())
                return knowledge_graph
            except:
                # If parsing fails, return a simple structure
                return {
                    "nodes": [
                        {"id": "1", "label": "Main Entity"},
                        {"id": "2", "label": "Related Concept"}
                    ],
                    "edges": [
                        {"source": "1", "target": "2", "label": "related to"}
                    ]
                }
        except Exception as e:
            return {
                "nodes": [
                    {"id": "1", "label": "Main Entity"},
                    {"id": "2", "label": "Related Concept"}
                ],
                "edges": [
                    {"source": "1", "target": "2", "label": "related to"}
                ]
            }