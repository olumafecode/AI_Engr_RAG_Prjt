"""Shared helpers for the evaluation scripts."""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from collections import deque
from pathlib import Path

from app.config import Settings

EVAL_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = EVAL_DIR / "questions.jsonl"
RESULTS_DIR = EVAL_DIR / "results"

CITATION_MARK = re.compile(r"\[\d+\]")
DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2212"), "-")


def load_questions() -> list[dict]:
    lines = QUESTIONS_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_chunk_texts(settings: Settings) -> dict[str, dict]:
    """chunk_id -> chunk record (text and metadata) from the index's chunks.jsonl."""
    path = settings.chroma_dir / "chunks.jsonl"
    if not path.is_file():
        raise SystemExit("No index found. Build it first with: python -m app.ingest")
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return {record["chunk_id"]: record for record in records}


def write_json(name: str, data) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_json(name: str):
    path = RESULTS_DIR / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def normalize(text: str) -> str:
    """Lower-case, unify Unicode dashes and spaces, and drop citation markers."""
    text = unicodedata.normalize("NFKC", text).translate(DASHES)
    return CITATION_MARK.sub(" ", text).lower()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[.,][0-9]+)*", normalize(text))


def token_f1(prediction: str, reference: str) -> float:
    predicted, gold = tokens(prediction), tokens(reference)
    if not predicted or not gold:
        return 0.0
    remaining = list(gold)
    overlap = 0
    for token in predicted:
        if token in remaining:
            remaining.remove(token)
            overlap += 1
    if overlap == 0:
        return 0.0
    precision, recall = overlap / len(predicted), overlap / len(gold)
    return round(2 * precision * recall / (precision + recall), 3)


def answer_words(text: str) -> int:
    """Words in an answer, not counting citation markers or stray punctuation."""
    return len([word for word in CITATION_MARK.sub(" ", text).split() if re.search(r"\w", word)])


def percentile(values: list[float], pct: float) -> float:
    """Linear interpolation between closest ranks (the same method as numpy's default)."""
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    position = (len(ordered) - 1) * pct / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


class TokenBudget:
    """Keeps requests to one model under a tokens-per-minute and requests-per-minute limit.

    Groq's free tier allows 8,000 tokens and 30 requests per minute per model, so the
    evaluation waits when the last 60 seconds of usage plus the next request would
    exceed a slightly lower budget.
    """

    def __init__(
        self, tokens_per_minute: int | None = None, requests_per_minute: int | None = None
    ) -> None:
        # Defaults suit Groq's free tier; paid tiers can raise them with these variables.
        self.tokens_per_minute = tokens_per_minute or int(
            os.getenv("EVAL_TOKENS_PER_MINUTE", "7000")
        )
        self.requests_per_minute = requests_per_minute or int(
            os.getenv("EVAL_REQUESTS_PER_MINUTE", "25")
        )
        self._events: deque[tuple[float, int]] = deque()
        self._sizes: list[int] = []

    def estimate(self) -> int:
        recent = self._sizes[-10:]
        return int(sum(recent) / len(recent)) if recent else 2500

    def wait(self) -> float:
        waited = 0.0
        while True:
            now = time.monotonic()
            while self._events and now - self._events[0][0] >= 60:
                self._events.popleft()
            used = sum(size for _, size in self._events)
            if (
                used + self.estimate() <= self.tokens_per_minute
                and len(self._events) < self.requests_per_minute
            ):
                return waited
            pause = max(60 - (now - self._events[0][0]) + 0.5, 0.5)
            time.sleep(pause)
            waited += pause

    def record(self, size: int | None) -> None:
        size = size or self.estimate()
        self._events.append((time.monotonic(), size))
        self._sizes.append(size)


class PacedChatModel:
    """Wraps a chat model so every request waits for room in the token budget."""

    def __init__(self, inner, budget: TokenBudget) -> None:
        self._inner = inner
        self._budget = budget
        self.name = inner.name

    def complete(self, system: str, user: str) -> str:
        self._budget.wait()
        try:
            return self._inner.complete(system, user)
        finally:
            self._budget.record(getattr(self._inner, "last_usage", None))
