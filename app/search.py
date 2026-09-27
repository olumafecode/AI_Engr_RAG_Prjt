"""Query the index from the command line to check retrieval.

Run from the project root:
    python -m app.search "How long is mandatory block leave?"
    python -m app.search "Minimum password length?" --k 3 --expect-doc VB-POL-002
    python -m app.search "Who do I call if my card is stolen?" --mode vector

Each result shows its cosine similarity with the question (vector) and its
keyword score (BM25). With --expect-doc, the command exits with an error unless
that document is in the results; CI uses this as a retrieval smoke test.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from app.config import Settings
from app.retrieval import IndexNotReadyError, Retriever


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Search the Veridane policy index.")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=None, help="number of results (default: TOP_K)")
    parser.add_argument("--mode", choices=["hybrid", "vector"], help="default: RETRIEVAL_MODE")
    parser.add_argument("--expect-doc", help="fail unless this doc ID is in the results")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.mode:
        settings = replace(settings, retrieval_mode=args.mode)
    try:
        retriever = Retriever(settings)
    except IndexNotReadyError as error:
        sys.exit(str(error))

    retrieval = retriever.search(args.question, args.k)
    gate = "pass" if retrieval.best_vector_score >= settings.relevance_threshold else "refuse"
    print(f"Question: {args.question}")
    print(
        f"Mode: {settings.retrieval_mode}. Best vector score {retrieval.best_vector_score:.3f} "
        f"(threshold {settings.relevance_threshold}: {gate})\n"
    )
    for rank, chunk in enumerate(retrieval.chunks, start=1):
        preview = " ".join(chunk.text.split())[:160]
        print(
            f"{rank}. vector {chunk.vector_score:.3f}  bm25 {chunk.lexical_score:5.2f}  "
            f"{chunk.chunk_id}  {chunk.metadata['section']}"
        )
        print(f"   {preview}\n")

    if args.expect_doc:
        found = any(chunk.metadata["doc_id"] == args.expect_doc for chunk in retrieval.chunks)
        if not found:
            count = len(retrieval.chunks)
            sys.exit(f"Expected {args.expect_doc} in the top {count} results; not found.")
        print(f"OK: {args.expect_doc} is in the top {len(retrieval.chunks)} results.")


if __name__ == "__main__":
    main()
