"""Build the vector index from the policy corpus.

Run from the project root:
    python -m app.ingest               # parse, chunk, embed, and store
    python -m app.ingest --dry-run     # parse and chunk only; no model download
    python -m app.ingest --strategy window --chunk-size 200 --chunk-overlap 30

Each run rebuilds the collection from scratch, so the index always matches
the corpus and settings it was built from. Alongside the Chroma files, the
run writes index_manifest.json and chunks.jsonl (one line per chunk) to
CHROMA_DIR for inspection.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime

from app.chunking import Chunk, chunk_corpus
from app.config import Settings
from app.corpus_utils import corpus_fingerprint
from app.embeddings import Embedder, get_embedder
from app.index_manifest import write_manifest
from app.parsing import parse_corpus
from app.vector_store import VectorStore


def build_index(
    settings: Settings, embedder: Embedder | None = None, dry_run: bool = False
) -> tuple[dict, list[Chunk]]:
    started = time.perf_counter()
    documents = parse_corpus(settings.corpus_dir)
    chunks = chunk_corpus(
        documents, settings.chunk_strategy, settings.chunk_size, settings.chunk_overlap
    )
    tokens = [chunk.token_count for chunk in chunks]
    manifest = {
        "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "corpus_fingerprint": corpus_fingerprint(settings.corpus_dir),
        "documents": len(documents),
        "chunks": len(chunks),
        "chunk_strategy": settings.chunk_strategy,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "tokens_per_chunk": {
            "min": min(tokens),
            "median": statistics.median(tokens),
            "max": max(tokens),
        },
        "collection": settings.collection_name,
    }
    if dry_run:
        return manifest, chunks

    embedder = embedder or get_embedder(settings)
    vectors = embedder.embed_documents([chunk.embedding_text for chunk in chunks])
    VectorStore(settings.chroma_dir, settings.collection_name).rebuild(chunks, vectors)

    manifest["embedding_model"] = embedder.name
    manifest["dimension"] = embedder.dimension
    manifest["build_seconds"] = round(time.perf_counter() - started, 2)
    write_manifest(settings, manifest)
    with (settings.chroma_dir / "chunks.jsonl").open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            record = {"chunk_id": chunk.chunk_id, **chunk.metadata(), "text": chunk.text}
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return manifest, chunks


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the Veridane policy vector index.")
    parser.add_argument("--dry-run", action="store_true", help="parse and chunk only")
    parser.add_argument("--strategy", choices=["heading", "window"])
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--chunk-overlap", type=int)
    args = parser.parse_args(argv)

    overrides = {
        "chunk_strategy": args.strategy,
        "chunk_size": args.chunk_size,
        "chunk_overlap": args.chunk_overlap,
    }
    settings = replace(
        Settings.from_env(), **{key: value for key, value in overrides.items() if value is not None}
    )
    manifest, chunks = build_index(settings, dry_run=args.dry_run)

    per_document = Counter(chunk.doc_id for chunk in chunks)
    for doc_id, count in sorted(per_document.items()):
        print(f"  {doc_id}: {count} chunks")
    token_stats = manifest["tokens_per_chunk"]
    print(
        f"\n{manifest['documents']} documents -> {manifest['chunks']} chunks "
        f"({manifest['chunk_strategy']}, size {manifest['chunk_size']}, "
        f"overlap {manifest['chunk_overlap']}); tokens per chunk: min {token_stats['min']}, "
        f"median {token_stats['median']}, max {token_stats['max']}"
    )
    if args.dry_run:
        print("Dry run: nothing was embedded or stored.")
    else:
        print(
            f"Embedded with {manifest['embedding_model']} ({manifest['dimension']} dimensions) "
            f"and stored in {settings.chroma_dir} in {manifest['build_seconds']} s."
        )


if __name__ == "__main__":
    main()
