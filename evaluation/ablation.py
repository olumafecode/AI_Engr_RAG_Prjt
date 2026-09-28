"""Retrieval ablations: how search settings change what reaches the model.

Run from the project root (needs a built index; no API key or LLM calls):
    python -m evaluation.ablation

Compares hybrid (vector + BM25) with vector-only search, heading-aware with
fixed-window chunking, and k = 3, 5, and 8, on the 24 in-scope questions:
- hit rate: an acceptable source document is among the excerpts;
- MRR: 1 / rank of the first excerpt from an acceptable source document;
- source coverage: share of the acceptable source documents that appear.
It also reports how well the best similarity score separates in-scope from
out-of-scope questions, which is what the relevance gate relies on.

Answer quality is measured once, for the deployed settings (evaluation.quality),
because each full run uses much of the free-tier daily token allowance.
"""

from __future__ import annotations

from dataclasses import replace

from app.config import Settings
from app.embeddings import get_embedder
from app.index_manifest import read_manifest
from app.ingest import build_index
from app.retrieval import Retriever
from evaluation.common import EVAL_DIR, load_questions, write_json
from evaluation.report import write_report

INDEX_DIR = EVAL_DIR / ".indexes"

CONFIGS = [
    ("Deployed: heading chunks, hybrid, k=5", "heading", "hybrid", 5),
    ("Heading chunks, vector only, k=5", "heading", "vector", 5),
    ("Heading chunks, hybrid, k=3", "heading", "hybrid", 3),
    ("Heading chunks, hybrid, k=8", "heading", "hybrid", 8),
    ("Window chunks (350/50), hybrid, k=5", "window", "hybrid", 5),
    ("Window chunks (350/50), vector only, k=5", "window", "vector", 5),
]


def retrieval_scores(doc_ids: list[str], gold: set[str]) -> dict:
    first = next((rank for rank, doc in enumerate(doc_ids, start=1) if doc in gold), None)
    return {
        "hit": first is not None,
        "reciprocal_rank": 1 / first if first else 0.0,
        "coverage": len(gold & set(doc_ids)) / len(gold) if gold else 0.0,
    }


def index_for(strategy: str, settings: Settings, embedder) -> Settings:
    """Use the main index for its own strategy; build others under evaluation/.indexes."""
    manifest = read_manifest(settings) or {}
    if (
        manifest.get("chunk_strategy") == strategy
        and manifest.get("embedding_model") == embedder.name
    ):
        return settings
    alternative = replace(settings, chroma_dir=INDEX_DIR / strategy, chunk_strategy=strategy)
    built = read_manifest(alternative) or {}
    if built.get("embedding_model") != embedder.name or built.get("chunk_strategy") != strategy:
        print(f"Building a {strategy} index for the comparison...", flush=True)
        build_index(alternative, embedder=embedder)
    return alternative


def main() -> None:
    settings = Settings.from_env()
    embedder = get_embedder(settings)
    questions = load_questions()
    in_scope = [q for q in questions if q["in_scope"]]
    out_of_scope = [q for q in questions if not q["in_scope"]]

    rows = []
    for label, strategy, mode, k in CONFIGS:
        config = replace(index_for(strategy, settings, embedder), retrieval_mode=mode, top_k=k)
        retriever = Retriever(config, embedder=embedder)
        per_question = []
        for question in in_scope:
            retrieval = retriever.search(question["question"], k)
            docs = [chunk.metadata["doc_id"] for chunk in retrieval.chunks]
            scores = retrieval_scores(docs, set(question["gold_docs"]))
            per_question.append({"id": question["id"], "type": question["type"], **scores})
        gate_in = [retriever.search(q["question"], 1).best_vector_score for q in in_scope]
        gate_out = [retriever.search(q["question"], 1).best_vector_score for q in out_of_scope]
        count = len(per_question)
        row = {
            "config": label,
            "chunk_strategy": strategy,
            "retrieval_mode": mode,
            "k": k,
            "hit_rate": round(sum(p["hit"] for p in per_question) / count, 3),
            "mrr": round(sum(p["reciprocal_rank"] for p in per_question) / count, 3),
            "source_coverage": round(sum(p["coverage"] for p in per_question) / count, 3),
            "missed": [p["id"] for p in per_question if not p["hit"]],
            "gate": {
                "in_scope_min": round(min(gate_in), 3),
                "out_of_scope_max": round(max(gate_out), 3),
                "out_of_scope_below_threshold": sum(
                    score < settings.relevance_threshold for score in gate_out
                ),
                "in_scope_below_threshold": sum(
                    score < settings.relevance_threshold for score in gate_in
                ),
            },
            "per_question": per_question,
        }
        rows.append(row)
        print(
            f"{label:44} hit {row['hit_rate']:.0%}  MRR {row['mrr']:.2f}  "
            f"coverage {row['source_coverage']:.0%}  missed {row['missed'] or '-'}",
            flush=True,
        )

    write_json(
        "ablation_results.json",
        {"threshold": settings.relevance_threshold, "questions": len(in_scope), "rows": rows},
    )
    write_report()
    print("\nFull report: evaluation/results/report.md")


if __name__ == "__main__":
    main()
