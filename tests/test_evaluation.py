"""Checks for the evaluation set and scoring code. No LLM calls."""

from app.corpus_utils import doc_id_from_filename, list_documents
from evaluation.ablation import retrieval_scores
from evaluation.common import TokenBudget, answer_words, load_questions, percentile, token_f1
from evaluation.judge import parse_verdict
from evaluation.metrics import enrich, latency_summary, summarize


def test_question_set_matches_the_plan(settings):
    questions = load_questions()
    assert len(questions) == 30
    assert len({q["id"] for q in questions}) == 30
    in_scope = [q for q in questions if q["in_scope"]]
    assert len(in_scope) == 24
    corpus = {doc_id_from_filename(p) for p in list_documents(settings.corpus_dir)}
    covered = {doc for q in in_scope for doc in q["gold_docs"]}
    assert covered == corpus  # every document is the source of at least one question
    assert all(q["gold_answer"] for q in questions)
    topics = " ".join(q["topic"] for q in in_scope).lower()
    for brief_topic in ("pto", "security", "expense", "remote work", "holidays"):
        assert brief_topic in topics


def test_token_f1_ignores_citations_and_dash_styles():
    assert token_f1("USD 90 per day [1].", "USD 90 per day.") == 1.0
    assert token_f1("VB\u2011POL\u2011004 applies", "VB-POL-004 applies") == 1.0
    assert token_f1("nothing alike", "USD 90 per day") == 0.0


def test_answer_words_skip_citation_markers():
    assert answer_words("Fourteen characters [1][2].") == 2


def test_percentile_matches_linear_interpolation():
    values = [100, 200, 300, 400, 500]
    assert percentile(values, 50) == 300
    assert percentile(values, 95) == 480


def test_budget_does_not_wait_when_there_is_room():
    budget = TokenBudget(tokens_per_minute=10000)
    budget.record(1000)
    assert budget.wait() == 0.0


def test_judge_reply_is_read_even_with_extra_text():
    reply = (
        'Here you go:\n```json\n{"grounded": true, "citations_correct": false, '
        '"correctness": "Partial", "explanation": "ok"}\n```'
    )
    verdict = parse_verdict(reply)
    assert verdict["grounded"] is True and verdict["correctness"] == "partial"


def _record(qid, in_scope, refused=False, grounded=True, cites=True, correctness="full"):
    record = {
        "id": qid,
        "question": "q",
        "in_scope": in_scope,
        "type": "fact",
        "gold_answer": "USD 90 per day",
        "gold_docs": ["VB-POL-012"] if in_scope else [],
        "answer": "I can only answer..." if refused else "USD 90 per day [1].",
        "refused": refused,
        "refusal_reason": "model_refusal" if refused else None,
        "citations": [] if refused else [{"doc_id": "VB-POL-012", "number": 1}],
        "retrieved": [{"doc_id": "VB-POL-012"}],
        "best_vector_score": 0.7,
        "error": None,
    }
    enrich(record, 200)
    if in_scope and not refused:
        record["judge"] = {
            "grounded": grounded,
            "citations_correct": cites,
            "correctness": correctness,
        }
    return record


def test_summary_counts_each_metric_against_its_target():
    records = [
        _record("a", True),
        _record("b", True, grounded=False, correctness="partial"),
        _record("c", True, refused=True),
        _record("d", False, refused=True),
    ]
    metrics = summarize(records, 200)["metrics"]
    assert metrics["groundedness"]["value"] == 0.5 and metrics["groundedness"]["n"] == 2
    assert metrics["false_refusal_rate"]["value"] == round(1 / 3, 4)
    assert metrics["out_of_scope_refused"]["met"] is True
    assert metrics["correct_full_or_partial"]["value"] == round(2 / 3, 4)
    assert metrics["retrieval_hit_rate"]["value"] == 1.0


def test_latency_summary_excludes_failed_requests():
    samples = [
        {"status": 200, "valid_json": True, "wall_ms": ms, "server_total_ms": ms - 100}
        for ms in (900, 1000, 1100)
    ] + [{"status": 503, "valid_json": False, "wall_ms": 50}]
    summary = latency_summary(samples)
    assert summary["metrics"]["latency_p50_ms"]["value"] == 1000
    assert summary["failed"] == 1


def test_retrieval_scores_find_first_acceptable_source():
    scores = retrieval_scores(
        ["VB-POL-001", "VB-POL-009", "VB-POL-002"], {"VB-POL-002", "VB-POL-009"}
    )
    assert scores["hit"] and scores["reciprocal_rank"] == 0.5 and scores["coverage"] == 1.0


def test_archiving_a_run_keeps_it_and_the_report_compares_runs(tmp_path):
    from evaluation.archive import archive_run
    from evaluation.common import write_json
    from evaluation.report import write_report

    settings = {
        "answer_model": "m",
        "reasoning_effort": "low",
        "judge_model": "j",
        "retrieval_mode": "hybrid",
        "top_k": 5,
        "chunk_strategy": "heading",
        "relevance_threshold": 0.55,
    }
    first = summarize([_record("a", True, correctness="partial")], 200)
    first["settings"] = settings
    write_json("quality_summary.json", first, tmp_path)
    write_json(
        "judge_agreement.json",
        {
            "answers": 1,
            "agreement": {"grounded": 1.0, "citations_correct": 1.0, "correctness": 1.0},
        },
        tmp_path,
    )
    moved = archive_run("run1", tmp_path)
    assert "quality_summary.json" in moved
    assert (tmp_path / "runs" / "run1" / "quality_summary.json").is_file()
    assert not (tmp_path / "quality_summary.json").exists()

    second = summarize([_record("a", True, correctness="full")], 200)
    second["settings"] = {**settings, "answer_style": "complete"}
    write_json("quality_summary.json", second, tmp_path)
    write_report(tmp_path)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "## Comparison with earlier runs" in report
    assert "run1: concise, Current run: complete" in report
    assert "made on the answers of run1" in report


def test_an_archived_run_can_be_restored_as_the_current_one(tmp_path):
    from evaluation.archive import archive_run, restore_run
    from evaluation.common import write_json

    summary = summarize([_record("a", True)], 200)
    summary["settings"] = {
        "answer_model": "m",
        "reasoning_effort": "low",
        "judge_model": "j",
        "retrieval_mode": "hybrid",
        "top_k": 5,
        "chunk_strategy": "heading",
        "relevance_threshold": 0.55,
        "answer_style": "concise",
    }
    write_json("quality_summary.json", summary, tmp_path)
    write_json("quality_results.json", {"records": [_record("a", True)]}, tmp_path)
    archive_run("run1", tmp_path)
    write_json(
        "quality_summary.json",
        {**summary, "settings": {**summary["settings"], "answer_style": "complete"}},
        tmp_path,
    )
    write_json("quality_results.json", {"records": [_record("a", True, cites=False)]}, tmp_path)

    import pytest

    with pytest.raises(FileExistsError):
        restore_run("run1", tmp_path)  # the current run must be archived first
    archive_run("run2-complete", tmp_path)
    restore_run("run1", tmp_path)
    assert (tmp_path / "quality_summary.json").is_file()
    assert not (tmp_path / "runs" / "run1").exists()
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "run2-complete: complete, Current run: concise" in report
    assert "Answers whose citations the judge rejected | 1 | 0 |" in report
