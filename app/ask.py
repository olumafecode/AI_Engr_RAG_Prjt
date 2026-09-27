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
    status = f"refused ({answer.refusal_reason})" if answer.refused else "answered"
    timing = answer.latency_ms
    print(
        f"\n{status}. Best vector score {answer.best_vector_score:.3f}. "
        f"Retrieval {timing['retrieval']} ms, generation {timing['generation']} ms, "
        f"total {timing['total']} ms. Model: {answer.model}."
    )


if __name__ == "__main__":
    main()
