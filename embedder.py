"""
embedder.py

Minimal embedding helper that loads OPENAI_API_KEY from environment (supports .env)
and returns embeddings for given text using OpenAI's Embeddings API.
"""

from __future__ import annotations

import os
from typing import List, Sequence

# Load .env if available (no-op if python-dotenv is not installed)
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

try:
    from openai import OpenAI
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "The 'openai' package is required. Install with: pip install openai"
    ) from exc


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in environment. Ensure it is set in your .env or shell."
        )
    return OpenAI(api_key=api_key)


_client = None  # lazily initialized


def _client_singleton() -> OpenAI:
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Return embedding vector for a single text.

    - Normalizes newlines per OpenAI guidance.
    - Raises ValueError for empty input.
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    cleaned = text.replace("\n", " ").strip()
    if not cleaned:
        raise ValueError("text is empty after trimming")
    client = _client_singleton()
    resp = client.embeddings.create(model=model, input=cleaned)
    return resp.data[0].embedding  # type: ignore[return-value]


def get_embeddings(texts: Sequence[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """Return embeddings for a sequence of texts."""
    if not isinstance(texts, (list, tuple)):
        raise ValueError("texts must be a list or tuple of strings")
    cleaned_list: List[str] = []
    for item in texts:
        if not isinstance(item, str):
            raise ValueError("each item in texts must be a string")
        cleaned = item.replace("\n", " ").strip()
        if not cleaned:
            raise ValueError("one of the texts is empty after trimming")
        cleaned_list.append(cleaned)
    client = _client_singleton()
    resp = client.embeddings.create(model=model, input=cleaned_list)
    return [d.embedding for d in resp.data]  # type: ignore[list-item]


if __name__ == "__main__":
    sample = "Hello world. This is an embedding test."
    vec = get_embedding(sample)
    print(f"Embedding length: {len(vec)}")
    print(vec[:8], "...")


