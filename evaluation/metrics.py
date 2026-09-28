"""Turn per-question evaluation records into metrics, checked against the targets
that were fixed in Stage 1 before anything was measured."""

from __future__ import annotations

from evaluation.common import answer_words, percentile, token_f1

# name: (target, comparison, description)
TARGETS = {
    "groundedness": (0.90, ">=", "Answered in-scope questions fully supported by the excerpts"),
    "citation_accuracy": (
        0.90,
        ">=",
        "Answered in-scope questions whose citations all support their statements and "
        "point only to acceptable source documents",
    ),
    "correct_full_or_partial": (
        0.85,
        ">=",
        "In-scope answers matching the reference fully or partly",
    ),
    "correct_full": (0.70, ">=", "In-scope answers matching the reference fully"),
    "out_of_scope_refused": (1.00, ">=", "Out-of-scope questions refused"),
    "false_refusal_rate": (0.05, "<=", "In-scope questions wrongly refused"),
    "retrieval_hit_rate": (
        0.95,
        ">=",
        "In-scope questions with an acceptable source in the excerpts",
    ),
    "length_compliance": (1.00, ">=", "Answers within the word limit"),
    "error_rate": (0.0, "<=", "Requests that failed"),
    "latency_p50_ms": (3000, "<=", "Median end-to-end time on the deployed app"),
    "latency_p95_ms": (6000, "<=", "95th percentile end-to-end time on the deployed app"),
}


def metric(name: str, value: float | None, n: int) -> dict:
    target, comparison, description = TARGETS[name]
    if value is None:
        met = None
    else:
        met = value >= target if comparison == ">=" else value <= target
    return {
        "value": value,
        "n": n,
        "target": target,
        "comparison": comparison,
        "met": met,
        "description": description,
    }


def _share(flags: list[bool]) -> float | None:
    return round(sum(flags) / len(flags), 4) if flags else None


def enrich(record: dict, max_words: int) -> dict:
    """Add the automatic, judge-free checks to one record."""
    retrieved_docs = [item["doc_id"] for item in record.get("retrieved", [])]
    cited_docs = sorted({citation["doc_id"] for citation in record.get("citations", [])})
    gold = set(record["gold_docs"])
    answered = not record.get("error") and not record.get("refused")
    record["cited_docs"] = cited_docs
    record["words"] = answer_words(record.get("answer", "")) if answered else 0
    if record["in_scope"]:
        record["retrieval_hit"] = (
            bool(gold & set(retrieved_docs)) if not record.get("error") else None
        )
        record["citation_docs_ok"] = (
            bool(cited_docs) and set(cited_docs) <= gold if answered else None
        )
        record["token_f1"] = token_f1(record["answer"], record["gold_answer"]) if answered else 0.0
    else:
        record["retrieval_hit"] = record["citation_docs_ok"] = record["token_f1"] = None
    return record


def summarize(records: list[dict], max_words: int) -> dict:
    in_scope = [r for r in records if r["in_scope"]]
    out_of_scope = [r for r in records if not r["in_scope"]]
    answered_in = [r for r in in_scope if not r.get("error") and not r.get("refused")]
    judged = [r for r in answered_in if r.get("judge")]
    answered_all = [r for r in records if not r.get("error") and not r.get("refused")]

    def correctness(record: dict) -> str:
        return record["judge"]["correctness"] if record.get("judge") else "incorrect"

    metrics = {
        "groundedness": metric(
            "groundedness", _share([r["judge"]["grounded"] for r in judged]), len(judged)
        ),
        "citation_accuracy": metric(
            "citation_accuracy",
            _share([r["judge"]["citations_correct"] and r["citation_docs_ok"] for r in judged]),
            len(judged),
        ),
        "correct_full_or_partial": metric(
            "correct_full_or_partial",
            _share([correctness(r) in ("full", "partial") for r in in_scope]),
            len(in_scope),
        ),
        "correct_full": metric(
            "correct_full", _share([correctness(r) == "full" for r in in_scope]), len(in_scope)
        ),
        "out_of_scope_refused": metric(
            "out_of_scope_refused",
            _share([bool(r.get("refused")) for r in out_of_scope]),
            len(out_of_scope),
        ),
        "false_refusal_rate": metric(
            "false_refusal_rate", _share([bool(r.get("refused")) for r in in_scope]), len(in_scope)
        ),
        "retrieval_hit_rate": metric(
            "retrieval_hit_rate",
            _share([r["retrieval_hit"] for r in in_scope if r["retrieval_hit"] is not None]),
            len([r for r in in_scope if r["retrieval_hit"] is not None]),
        ),
        "length_compliance": metric(
            "length_compliance",
            _share([r["words"] <= max_words for r in answered_all]),
            len(answered_all),
        ),
        "error_rate": metric(
            "error_rate", _share([bool(r.get("error")) for r in records]), len(records)
        ),
    }

    by_type: dict[str, dict] = {}
    for kind in sorted({r["type"] for r in in_scope}):
        group = [r for r in in_scope if r["type"] == kind]
        by_type[kind] = {
            "questions": len(group),
            "correct_full_or_partial": _share(
                [correctness(r) in ("full", "partial") for r in group]
            ),
            "retrieval_hit_rate": _share([bool(r["retrieval_hit"]) for r in group]),
        }

    in_scores = [r["best_vector_score"] for r in in_scope if r.get("best_vector_score") is not None]
    out_scores = [
        r["best_vector_score"] for r in out_of_scope if r.get("best_vector_score") is not None
    ]
    return {
        "metrics": metrics,
        "counts": {
            "questions": len(records),
            "in_scope": len(in_scope),
            "out_of_scope": len(out_of_scope),
            "answered_in_scope": len(answered_in),
            "judged": len(judged),
            "judge_errors": len([r for r in answered_in if r.get("judge_error")]),
        },
        "by_type": by_type,
        "token_f1_mean": _share([r["token_f1"] for r in answered_in]),
        "refusal_reasons": {
            reason: len([r for r in records if r.get("refusal_reason") == reason])
            for reason in ("no_relevant_context", "model_refusal", "no_citations")
        },
        "gate_scores": {
            "in_scope_min": min(in_scores) if in_scores else None,
            "in_scope_median": round(percentile(in_scores, 50), 3) if in_scores else None,
            "out_of_scope_max": max(out_scores) if out_scores else None,
            "out_of_scope_median": round(percentile(out_scores, 50), 3) if out_scores else None,
        },
    }


def latency_summary(samples: list[dict]) -> dict:
    ok = [s for s in samples if s["status"] == 200 and s.get("valid_json")]
    wall = [s["wall_ms"] for s in ok]
    server = [s["server_total_ms"] for s in ok if s.get("server_total_ms") is not None]
    failed = len(samples) - len(ok)
    p50 = round(percentile(wall, 50)) if wall else None
    p95 = round(percentile(wall, 95)) if wall else None
    return {
        "metrics": {
            "latency_p50_ms": metric("latency_p50_ms", p50, len(wall)),
            "latency_p95_ms": metric("latency_p95_ms", p95, len(wall)),
            "error_rate": metric(
                "error_rate", round(failed / len(samples), 4) if samples else None, len(samples)
            ),
        },
        "wall_ms": {
            "min": min(wall) if wall else None,
            "mean": round(sum(wall) / len(wall)) if wall else None,
            "max": max(wall) if wall else None,
        },
        "server_ms": {
            "p50": round(percentile(server, 50)) if server else None,
            "p95": round(percentile(server, 95)) if server else None,
        },
        "requests": len(samples),
        "failed": failed,
    }
