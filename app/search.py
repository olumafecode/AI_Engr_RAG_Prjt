"""Query the vector index from the command line to check retrieval.

Run from the project root:
    python -m app.search "How long is mandatory block leave?"
    python -m app.search "Minimum password length?" --k 3 --expect-doc VB-POL-002

With --expect-doc, the command exits with an error unless that document
appears in the top-k results. CI uses this as a retrieval smoke test.
"""

from __future__ import annotations

import argparse
import sys

from app.config import Settings
from app.retrieval import IndexNotReadyError, Retriever


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Search the Veridane policy index.")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=None, help="number of results (default: TOP_K)")
    parser.add_argument("--expect-doc", help="fail unless this doc ID is in the results")
    args = parser.parse_args(argv)

    try:
        retriever = Retriever(Settings.from_env())
    except IndexNotReadyError as error:
        sys.exit(str(error))

    results = retriever.search(args.question, args.k)
    print(f"Question: {args.question}\n")
    for rank, result in enumerate(results, start=1):
        meta = result.metadata
        preview = " ".join(result.text.split())[:160]
        print(f"{rank}. {result.score:.3f}  {result.chunk_id}  {meta['section']}")
        print(f"   {preview}\n")

    if args.expect_doc:
        found = any(result.metadata["doc_id"] == args.expect_doc for result in results)
        if not found:
            sys.exit(f"Expected {args.expect_doc} in the top {len(results)} results; not found.")
        print(f"OK: {args.expect_doc} is in the top {len(results)} results.")


if __name__ == "__main__":
    main()
