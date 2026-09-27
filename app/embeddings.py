"""Embedding models behind one small interface.

- FastEmbedEmbedder runs BAAI/bge-small-en-v1.5 locally through ONNX Runtime.
  The model (about 67 MB) is downloaded once into MODEL_CACHE_DIR.
- HashEmbedder is a deterministic bag-of-words stand-in with no downloads.
  It is used by the test suite and can be selected with EMBEDDING_MODEL=hash.
"""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Protocol

from app.config import Settings


class Embedder(Protocol):
    name: str
    dimension: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class FastEmbedEmbedder:
    def __init__(self, model_name: str, cache_dir: Path, query_prefix: str = "") -> None:
        import onnxruntime
        from fastembed import TextEmbedding  # imported lazily: it loads ONNX Runtime

        onnxruntime.set_default_logger_severity(3)  # hide hardware-discovery warnings

        cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir))
        self.name = model_name
        self.dimension = self._model.embedding_size
        self._query_prefix = query_prefix

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts, batch_size=32)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.embed([self._query_prefix + text]))).tolist()


class HashEmbedder:
    """Signed feature hashing of lower-cased words, L2-normalized."""

    name = "hash"

    def __init__(self, dimension: int = 256) -> None:
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.md5(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            vector[index] += 1.0 if digest[4] % 2 == 0 else -1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_embedder(settings: Settings) -> Embedder:
    if settings.embedding_model == "hash":
        return HashEmbedder()
    return FastEmbedEmbedder(
        settings.embedding_model, settings.model_cache_dir, settings.query_prefix
    )
