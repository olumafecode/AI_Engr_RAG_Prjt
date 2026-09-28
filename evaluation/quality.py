"""Answer every evaluation question with the production pipeline, then judge the answers.

Run from the project root (needs GROQ_API_KEY in .env and a built index):
    python -m evaluation.quality            # resumes where it stopped
    python -m evaluation.quality --fresh    # starts again from question 1

It uses the same code, settings, and index as the web app, but runs in-process
so the judge can see the full text of every excerpt the answering model saw.
Requests are paced to stay inside Groq's free-tier limits (8,000 tokens per
minute per model), so a full run takes about 15 to 20 minutes. Progress is
saved after every question, so an interrupted run can simply be restarted.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import asdict

from app.assistant import PolicyAssistant
from app.config import Settings
from app.generation import GroqChatModel, LLMNotConfiguredError, LLMUnavailableError
from app.index_manifest import read_manifest
from evaluation.common import (
    PacedChatModel,
    TokenBudget,
    load_chunk_texts,
    load_questions,
    read_json,
    write_json,
)
from evaluation.judge import judge, make_judge_model
from evaluation.metrics import enrich, summarize
from evaluation.report import write_report

RESULTS = "quality_results.json"


def run_settings(settings: Settings) -> dict:
    manifest = read_manifest(settings) or {}
    return {
        "answer_model": settings.llm_model,
        "reasoning_effort": settings.llm_reasoning_effort,
        "answer_style": settings.answer_style,
        "judge_model": settings.judge_model,
        "embedding_model": manifest.get("embedding_model"),
        "chunk_strategy": manifest.get("chunk_strategy"),
        "chunks": manifest.get("chunks"),
        "retrieval_mode": settings.retrieval_mode,
        "top_k": settings.top_k,
        "relevance_threshold": settings.relevance_threshold,
        "max_answer_words": settings.max_answer_words,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the answer-quality evaluation.")
    parser.add_argument("--fresh", action="store_true", help="ignore saved progress")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    questions = load_questions()
    chunks = load_chunk_texts(settings)
    try:
        answer_model = PacedChatModel(GroqChatModel(settings, max_retries=6), TokenBudget())
        judge_model = PacedChatModel(make_judge_model(settings), TokenBudget())
    except LLMNotConfiguredError as error:
        sys.exit(str(error))
    assistant = PolicyAssistant(settings, chat_model=answer_model)

    saved = (
        {} if args.fresh else {r["id"]: r for r in (read_json(RESULTS) or {}).get("records", [])}
    )
    records = []
    started = time.perf_counter()
    for number, question in enumerate(questions, start=1):
        record = saved.get(question["id"])
        needs_judge = record and record["in_scope"] and not record.get("refused")
        if record and not record.get("error") and (not needs_judge or record.get("judge")):
            records.append(record)
            continue

        record = dict(question)
        try:
            answer = assistant.answer(question["question"])
            record.update(
                {k: v for k, v in asdict(answer).items() if k not in ("question", "model")}
            )
            record["error"] = None
            if record["refusal_reason"] == "no_citations":
                record["raw_replies"] = assistant.last_raw_replies
        except LLMUnavailableError as error:
            record.update(
                {
                    "answer": "",
                    "refused": False,
                    "refusal_reason": None,
                    "citations": [],
                    "retrieved": [],
                    "best_vector_score": None,
                    "latency_ms": {},
                    "error": str(error),
                }
            )
        enrich(record, settings.max_answer_words)

        if record["in_scope"] and not record["error"] and not record["refused"]:
            try:
                record["judge"] = judge(record, chunks, judge_model)
                record["judge_error"] = None
            except (ValueError, LLMUnavailableError) as error:
                record["judge"], record["judge_error"] = None, str(error)

        records.append(record)
        status = (
            "ERROR"
            if record["error"]
            else (f"refused ({record['refusal_reason']})" if record["refused"] else "answered")
        )
        verdict = record.get("judge") or {}
        print(
            f"[{number:2}/{len(questions)}] {record['id']} {record['type']:12} {status:32} "
            f"{verdict.get('correctness', ''):9} {time.perf_counter() - started:6.0f} s",
            flush=True,
        )
        write_json(RESULTS, {"settings": run_settings(settings), "records": records})

    summary = summarize(records, settings.max_answer_words)
    summary["settings"] = run_settings(settings)
    write_json("quality_summary.json", summary)
    write_report()

    print("\nMetric                     Result   Target  Met")
    for name, item in summary["metrics"].items():
        value = "n/a" if item["value"] is None else f"{item['value']:.0%}"
        target = f"{item['comparison']} {item['target']:.0%}"
        print(f"{name:26} {value:>7}  {target:>7}  {item['met']}  (n={item['n']})")
    print("\nFull report: evaluation/results/report.md")


if __name__ == "__main__":
    main()
