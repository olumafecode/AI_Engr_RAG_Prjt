"""A small BM25 keyword index, used alongside vector search (hybrid retrieval).

Vector search matches meaning; BM25 matches the exact words a question uses,
such as "stolen card" or "CCTV". Combining the two recovers passages that one
method alone ranks too low.
"""

from __future__ import annotations

import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "how", "i", "if", "in", "is", "it", "its", "me", "my", "of", "on", "or", "our", "should",
    "that", "the", "their", "this", "to", "was", "we", "what", "when", "where", "which",
    "who", "will", "with", "you", "your",
}  # fmt: skip


def _normalize(word: str) -> str:
    """Very light plural folding: 'policies' -> 'policy', 'passwords' -> 'password'."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    return [
        _normalize(word) for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOPWORDS
    ]


class BM25:
    """Okapi BM25 over a fixed list of documents."""

    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self._k1, self._b = k1, b
        self._term_counts = [Counter(tokenize(document)) for document in documents]
        self._lengths = [sum(counts.values()) for counts in self._term_counts]
        self._average_length = sum(self._lengths) / max(len(self._lengths), 1)
        document_frequency = Counter(term for counts in self._term_counts for term in counts)
        total = len(documents)
        self._idf = {
            term: math.log(1 + (total - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def scores(self, query: str) -> list[float]:
        terms = [term for term in tokenize(query) if term in self._idf]
        results = []
        for counts, length in zip(self._term_counts, self._lengths, strict=True):
            score = 0.0
            for term in terms:
                frequency = counts.get(term, 0)
                if frequency:
                    norm = self._k1 * (1 - self._b + self._b * length / self._average_length)
                    score += self._idf[term] * frequency * (self._k1 + 1) / (frequency + norm)
            results.append(score)
        return results

    def top(self, query: str, n: int) -> list[tuple[int, float]]:
        """Indices and scores of the n best matches with a score above zero."""
        ranked = sorted(enumerate(self.scores(query)), key=lambda item: (-item[1], item[0]))
        return [(index, score) for index, score in ranked[:n] if score > 0]
