"""Ask the assistant a question from the command line (needs GROQ_API_KEY in .env).

Run from the project root:
    python -m app.ask "How long is mandatory block leave?"
"""

from __future__ import annotations

import argparse
import sys

from app.assistant import PolicyAssistant
from app.config import Settings
from app.generation import LLMNotConfiguredError, LLMUnavailableError
from app.retrieval import IndexNotReadyError


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ask the Veridane Policy Assistant.")
    parser.add_argument("question")
    args = parser.parse_args(argv)

    try:
        answer = PolicyAssistant(Settings.from_env()).answer(args.question)
    except (IndexNotReadyError, LLMNotConfiguredError, LLMUnavailableError) as error:
        sys.exit(str(error))

    print(f"Question: {answer.question}\n")
    print(answer.answer)
    if answer.citations:
        print("\nSources:")
        for citation in answer.citations:
            print(f"  [{citation.number}] {citation.doc_id} {citation.title}, {citation.section}")
    print("\nRetrieved excerpts (sent to the model unless the relevance gate refused):")
    for rank, item in enumerate(answer.retrieved, start=1):
        print(
            f"  S{rank}  {item['chunk_id']:15} vector {item['vector_score']:.3f}  "
            f"bm25 {item['lexical_score']:5.2f}  {item['section']}"
            + (f"  (added: {item['added_for']})" if item.get("added_for") else "")
        )
    status = f"refused ({answer.refusal_reason})" if answer.refused else "answered"
    timing = answer.latency_ms
    print(
        f"\n{status}. Best vector score {answer.best_vector_score:.3f}. "
        f"Retrieval {timing['retrieval']} ms, generation {timing['generation']} ms, "
        f"total {timing['total']} ms. Model: {answer.model}."
    )


if __name__ == "__main__":
    main()
