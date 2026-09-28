"""Measure end-to-end latency of the deployed app.

Run from the project root:
    python -m evaluation.latency --url https://veridane-policy-assistant.onrender.com

1. Calls /health and times it. If the service was asleep, this is the wake-up time.
2. Waits until the warm-up has finished, so every timed request is a warm one.
3. Sends the first 20 in-scope questions to POST /chat, one at a time, and times each
   from sending the request to receiving the full response.

Requests are spaced 20 seconds apart: the deployed app and this script share the
Groq account's limit of 8,000 tokens per minute, and a rate-limited request would
measure the rate limit rather than the app. The spacing also keeps the free
instance awake. Do not run this at the same time as evaluation.quality.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request

from evaluation.common import load_questions, write_json
from evaluation.metrics import latency_summary
from evaluation.report import write_report


def call(method: str, url: str, body: dict | None = None, timeout: float = 120) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    started = time.perf_counter()
    status, payload, error = None, b"", None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, payload = response.status, response.read()
    except urllib.error.HTTPError as failure:
        status, payload = failure.code, failure.read()
    except (urllib.error.URLError, TimeoutError, OSError) as failure:
        error = str(failure)
    elapsed = round((time.perf_counter() - started) * 1000)
    try:
        parsed = json.loads(payload) if payload else None
    except json.JSONDecodeError:
        parsed = None
    return {"status": status, "json": parsed, "wall_ms": elapsed, "error": error}


def wait_until_ready(base: str, limit_seconds: int = 180) -> dict:
    deadline = time.monotonic() + limit_seconds
    while True:
        health = call("GET", f"{base}/health")
        state = ((health["json"] or {}).get("warmup") or {}).get("state")
        if health["status"] == 200 and state in ("ready", "off", "failed"):
            return health
        if time.monotonic() > deadline:
            return health
        time.sleep(5)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Measure latency of the deployed app.")
    parser.add_argument("--url", required=True, help="base URL of the deployed app")
    parser.add_argument("--n", type=int, default=20, help="number of timed questions (10 to 20)")
    parser.add_argument("--pause", type=float, default=20, help="seconds between requests")
    args = parser.parse_args(argv)
    base = args.url.rstrip("/")

    first = call("GET", f"{base}/health", timeout=180)
    uptime = (first["json"] or {}).get("uptime_seconds")
    print(
        f"First /health: HTTP {first['status']} in {first['wall_ms'] / 1000:.1f} s "
        f"(service uptime {uptime} s)"
    )
    ready = wait_until_ready(base)
    warmup = (ready["json"] or {}).get("warmup")
    print(f"Warm-up: {warmup}")

    questions = [q for q in load_questions() if q["in_scope"]][: args.n]
    samples = []
    for number, question in enumerate(questions, start=1):
        if number > 1:
            time.sleep(args.pause)
        result = call("POST", f"{base}/chat", {"question": question["question"]})
        body = result["json"] if isinstance(result["json"], dict) else {}
        sample = {
            "id": question["id"],
            "status": result["status"],
            "valid_json": "answer" in body,
            "wall_ms": result["wall_ms"],
            "server_total_ms": (body.get("latency_ms") or {}).get("total"),
            "server_latency_ms": body.get("latency_ms"),
            "refused": body.get("refused"),
            "error": result["error"] or body.get("error"),
        }
        samples.append(sample)
        print(
            f"[{number:2}/{len(questions)}] {question['id']} HTTP {sample['status']} "
            f"{sample['wall_ms']:6d} ms  server {sample['server_total_ms']} ms",
            flush=True,
        )

    summary = latency_summary(samples)
    summary["url"] = base
    summary["pause_seconds"] = args.pause
    summary["first_health"] = {
        "wall_ms": first["wall_ms"],
        "status": first["status"],
        "uptime_seconds": uptime,
        "note": "a cold start (wake-up) if uptime_seconds is small",
    }
    summary["warmup"] = warmup
    write_json("latency_results.json", samples)
    write_json("latency_summary.json", summary)
    write_report()

    metrics = summary["metrics"]
    print(
        f"\np50 {metrics['latency_p50_ms']['value']} ms (target <= 3000), "
        f"p95 {metrics['latency_p95_ms']['value']} ms (target <= 6000), "
        f"failed {summary['failed']} of {summary['requests']}"
    )
    print("Full report: evaluation/results/report.md")


if __name__ == "__main__":
    main()
