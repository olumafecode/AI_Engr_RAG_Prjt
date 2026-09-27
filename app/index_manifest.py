"""The index manifest records how and from what the vector index was built."""

from __future__ import annotations

import json

from app.config import Settings
from app.corpus_utils import corpus_fingerprint

MANIFEST_NAME = "index_manifest.json"


def read_manifest(settings: Settings) -> dict | None:
    path = settings.chroma_dir / MANIFEST_NAME
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(settings: Settings, manifest: dict) -> None:
    path = settings.chroma_dir / MANIFEST_NAME
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def index_status(settings: Settings) -> dict:
    """Summary used by /health: whether the index exists and matches the current corpus."""
    manifest = read_manifest(settings)
    if manifest is None:
        return {"built": False}
    return {
        "built": True,
        "chunks": manifest["chunks"],
        "embedding_model": manifest["embedding_model"],
        "chunk_strategy": manifest["chunk_strategy"],
        "up_to_date": manifest["corpus_fingerprint"] == corpus_fingerprint(settings.corpus_dir),
    }
