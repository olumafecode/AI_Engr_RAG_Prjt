"""LLM-as-judge for groundedness, citation accuracy, and answer correctness.

The judge is a larger model (openai/gpt-oss-120b) than the one that writes the
answers (openai/gpt-oss-20b), and it sees exactly the excerpts the answering
model saw. Its verdicts are checked against hand labels (see review.py).
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

from app.config import Settings
from app.generation import GroqChatModel

JUDGE_SYSTEM = (
    "You are a strict evaluator of a question-answering system for Veridane Bank's internal "
    "policies. You check the system's answer against the evidence it was given. "
    "Reply with a single JSON object and no other text."
)

JUDGE_TEMPLATE = """QUESTION:
{question}

REFERENCE ANSWER (written by the evaluator; use it only for "correctness"):
{gold}

EXCERPTS GIVEN TO THE SYSTEM:
{excerpts}

SYSTEM ANSWER:
{answer}

CITATIONS IN THE SYSTEM ANSWER:
{citations}

Evaluate the SYSTEM ANSWER:
1. "grounded": true only if every factual statement in the SYSTEM ANSWER is stated in, or \
directly follows from, the EXCERPTS. Ignore the reference answer for this check. Different \
wording is fine; added facts that are not in the excerpts are not.
2. "citations_correct": true only if each citation points to an excerpt that supports the \
statement it is attached to, and no citation points to an excerpt that does not support its \
statement. A citation at the end of a sentence or a short paragraph covers that sentence or \
paragraph.
3. "correctness": compare with the REFERENCE ANSWER. "full" if the answer contains all of its \
key facts and nothing that contradicts them; "partial" if it contains some key facts and \
nothing that contradicts them; "incorrect" if it misses the key facts or contradicts them.

Reply with this JSON object:
{{"grounded": true or false, "unsupported_statements": [strings],
"citations_correct": true or false, "citation_problems": [strings],
"correctness": "full" or "partial" or "incorrect", "explanation": "one or two sentences"}}"""

CORRECTNESS = ("full", "partial", "incorrect")


def judge_settings(settings: Settings, reasoning_effort: str = "medium") -> Settings:
    return replace(
        settings,
        llm_model=settings.judge_model,
        llm_reasoning_effort=reasoning_effort,
        llm_max_tokens=3000,
    )


def make_judge_model(settings: Settings) -> GroqChatModel:
    return GroqChatModel(judge_settings(settings), max_retries=6)


def format_excerpts(retrieved: list[dict], chunks: dict[str, dict]) -> str:
    blocks = []
    for label, item in enumerate(retrieved, start=1):
        record = chunks.get(item["chunk_id"], {})
        header = f"[S{label}] {record.get('title', '')} ({item['doc_id']}), {item['section']}"
        blocks.append(f"{header}\n{record.get('text', '(text not found)')}")
    return "\n\n".join(blocks)


def format_citations(citations: list[dict], retrieved: list[dict]) -> str:
    labels = {item["chunk_id"]: f"S{rank}" for rank, item in enumerate(retrieved, start=1)}
    lines = [
        f"[{c['number']}] -> {labels.get(c['chunk_id'], '?')} ({c['doc_id']}, {c['section']})"
        for c in citations
    ]
    return "\n".join(lines) or "(none)"


def build_judge_prompt(record: dict, chunks: dict[str, dict]) -> str:
    return JUDGE_TEMPLATE.format(
        question=record["question"],
        gold=record["gold_answer"],
        excerpts=format_excerpts(record["retrieved"], chunks),
        answer=record["answer"],
        citations=format_citations(record["citations"], record["retrieved"]),
    )


def parse_verdict(reply: str) -> dict:
    """Read the judge's JSON, tolerating text or code fences around it."""
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object in judge reply: {reply[:200]!r}")
    data = json.loads(match.group(0))
    correctness = str(data.get("correctness", "")).strip().lower()
    if correctness not in CORRECTNESS or not isinstance(data.get("grounded"), bool):
        raise ValueError(f"Judge reply is missing required fields: {data}")
    return {
        "grounded": data["grounded"],
        "unsupported_statements": list(data.get("unsupported_statements") or []),
        "citations_correct": bool(data.get("citations_correct")),
        "citation_problems": list(data.get("citation_problems") or []),
        "correctness": correctness,
        "explanation": str(data.get("explanation", "")),
    }


def judge(record: dict, chunks: dict[str, dict], model) -> dict:
    """Ask the judge once, and once more if its reply cannot be read."""
    prompt = build_judge_prompt(record, chunks)
    error = None
    for _ in range(2):
        try:
            return parse_verdict(model.complete(JUDGE_SYSTEM, prompt))
        except (ValueError, json.JSONDecodeError) as problem:
            error = problem
    raise ValueError(f"Judge reply could not be read twice: {error}")
