# Design and Evaluation

This document records the design decisions behind the Veridane Policy Assistant and the results of its evaluation. Sections marked as planned are confirmed or revised once the relevant stage is built and measured.

## Overview

The Veridane Policy Assistant answers staff questions about the policies of Veridane Bank. It retrieves the most relevant passages from a corpus of 14 policy documents, passes them to a language model with instructions to answer only from that evidence, and returns an answer that cites the document and section each claim comes from. Questions outside the corpus are refused.

## Architecture

```
Ingestion (built in Stage 2; runs at build time)
  corpus/ (md, txt, html, pdf)
    -> parse each format into sections with metadata and citation anchors
    -> clean (Unicode, whitespace, Markdown markup, PDF footers and glyphs)
    -> chunk: one chunk per section; long sections split into
       350-token windows of whole sentences with 50-token overlap
    -> embed "title (doc ID), section" + chunk text (bge-small-en-v1.5, local ONNX)
    -> store vectors, text, and metadata in Chroma (cosine distance)
    -> write index_manifest.json and chunks.jsonl

Question answering (built in Stage 3; per request)
  POST /chat {"question": ...}
    -> embed the question; score every chunk in Chroma (cosine)
    -> score every chunk with BM25 keywords
    -> fuse the two rankings with reciprocal rank fusion; keep the top 5
    -> relevance gate: refuse without calling the LLM if the best
       cosine similarity is below 0.55
    -> prompt: rules, then excerpts labeled [S1]..[S5] with doc ID,
       title, version, and section, then the question
    -> LLM (Groq, openai/gpt-oss-20b, reasoning effort low,
       temperature 0, seed 42, at most 1024 completion tokens)
    -> guardrails in code: detect refusals, drop citation labels that
       were not retrieved, renumber the rest [1], [2]..., retry once if
       an answer has no citation (then refuse), trim to 200 words
    -> JSON: answer, refusal status and reason, numbered citations
       (doc ID, title, section, snippet, link), retrieved chunk scores,
       latency for retrieval, generation, and total
```

## Design Decisions

| Component | Choice | Reason |
|---|---|---|
| Web framework | Flask with gunicorn | Maps directly onto the required `/`, `/chat`, and `/health` routes and stays small enough for a free host. |
| Parsing | One parser per format: YAML front matter (md), header block (txt), meta tags (html), header table (pdf) | Every document ends up with the same metadata and a list of sections, whatever its format. Each document also gets a generated "Document information" section, so questions such as "who owns the KYC policy?" can be answered from retrieval. |
| PDF extraction | pdfplumber, with tables extracted row by row | Plain text extraction scrambled table cells into one cell per line, which broke tables such as the KYC tier limits. Extracting tables separately keeps each row intact ("2 \| Tier 1 plus... \| USD 2,000 \| USD 1,000"). Running footers and unmapped bullet glyphs are removed during cleaning. |
| Chunking | One chunk per section; sections over 350 tokens are split into windows of whole sentences with 50-token overlap | Policy sections are short and self-contained (median 63 tokens), so a section is a natural unit of meaning and makes citations precise. Windows only apply to the one section that exceeds the limit (the roles table in the company profile). A fixed-window strategy is also implemented for comparison. |
| Token counting | Regex tokenizer (words, numbers, and punctuation marks each count as one) | Needs no download and gives identical counts on every machine. It slightly undercounts the model's WordPiece tokens, so the 350 limit leaves headroom under bge-small's 512-token input limit. |
| Embedding model | BAAI/bge-small-en-v1.5 through fastembed | Free, runs locally with no rate limits, gives deterministic vectors, and uses ONNX instead of PyTorch, so it fits in the 512 MB of a free Render instance. Each chunk is embedded with a short header ("title (doc ID), section") so that short chunks keep their context. Queries use the retrieval instruction recommended for bge models. |
| Vector store | Chroma, persistent and local, cosine distance | Named in the brief, file-based, and needs no separate service. The index is rebuilt from scratch on every run so it always matches the corpus; a manifest records the settings and a corpus fingerprint, and `/health` reports whether the index is out of date. |
| Retrieval | Hybrid: vector similarity and BM25 keyword scores, fused with reciprocal rank fusion (k = 60, top 30 of each list), top 5 kept | In the calibration run, vector search alone ranked "Counterfeit notes" first for "Who do I call if my card is stolen?", because the answer sits in a long contacts table. Keyword matching on "stolen" and "card" pulls up the Fraud Desk passages. RRF combines the two rankings without having to put cosine and BM25 scores on the same scale. A vector-only mode is kept for the ablation. |
| Top-k | k = 5 | Covers questions that need two documents without flooding the prompt. Confirmed or changed by the ablation in the evaluation. |
| Relevance gate | Refuse without calling the LLM when the best cosine similarity is below 0.55 | Set from a calibration run (next section). The gate is deliberately cautious: it only blocks questions that are clearly unrelated, because a wrongly refused policy question cannot be recovered, while a borderline question that passes still meets the prompt's refusal rule. |
| LLM | Groq free tier, openai/gpt-oss-20b, reasoning effort low, temperature 0, seed 42 | The original choice, llama-3.1-8b-instant, was retired from Groq's free tier on 16 August 2026, and the first live request returned `model_not_found`. Groq's recommended replacement is gpt-oss-20b. It is a reasoning model whose hidden reasoning tokens count against the completion budget, so reasoning effort is set to low and the budget raised to 1024 tokens; the 200-word answer limit is still enforced in code. An empty reply is reported as an error rather than treated as a refusal. Temperature 0 with a fixed seed keeps answers as repeatable as the API allows, and the model name is a setting, so another OpenAI-compatible model can be swapped in without code changes. |
| Prompt format | System rules, then excerpts labeled [S1] to [S5] with doc ID, title, version, and section, then the question | Short labels are easy for the model to cite and easy for code to check. The rules require a citation on every sentence, an answer whenever any excerpt contains the information, the exact refusal sentence only when none does or the question concerns another organization, the current rule unless the question asks what changed (Revision History excerpts answer those), plain text without Markdown, and at most 200 words. The first live run with gpt-oss-20b refused "What changed in the latest version of the password policy?" even though the revision history is ranked in the top five, and bolded one answer; the rules for answering, revision history, and plain text were made explicit after that run. The next run showed the real cause: the revision history was not among the five excerpts, so the refusal was correct behaviour for the evidence the model had. Questions about changes match a policy's topic more closely than its terse version notes, so a retrieval rule now adds the top-ranked document's Revision History chunk as a sixth excerpt whenever the question asks about changes, updates, or earlier values. `python -m app.ask` marks such excerpts as added. Instructions inside excerpts or questions are to be ignored.  After the first evaluation run, the answer-detail and citation rules were made more explicit (the "complete" answer style, now the default): the model is asked for every condition, exception, approval, limit, deadline, and contact that the excerpts attach to the answer, and to end each sentence with its labels in exactly the form [S2] or [S1][S3]. The first run's wording is kept as the "concise" style, and `ANSWER_STYLE=concise` restores it exactly; a test checks it against the saved text. Citations written in other brackets, such as (S2), are now also accepted, and the raw replies are logged whenever an answer is refused for lack of citations.|
| Guardrails | Relevance gate, prompt refusal rule, output token cap, and code checks after generation | Code drops citation labels that were not retrieved, renumbers the rest, retries once if an answer has no citations and refuses if it still has none, and trims answers over 200 words at a sentence boundary. Refusal and citation rules therefore do not depend on the model alone. |
| Source links | `/docs/<doc_id>` serves each policy: PDFs and HTML as the original files, Markdown and text rendered with the same section anchors used by the chunks | Every citation link opens the source at the cited section (for example `#41-minimum-requirements-by-account-type`, or `#page=3` for PDFs). |
| Hosting | Render free web service, defined in `render.yaml` | Named in the brief. The index is built during Render's build step because the running service's filesystem is not persistent. One gunicorn worker with two threads keeps memory inside 512 MB, the model loads in the background at start-up, and Render auto-deploy is off so that deploys happen only through the CI deploy hook after tests pass. |
| CI/CD | GitHub Actions | Lint, build check, and tests on every push and pull request; deploy on `main`. |

## Corpus

The application answers staff questions about the policies of Veridane Bank, a fictional commercial bank. Using a fictional organization means the corpus can be included in the repository without licensing concerns. It also means the model has no outside knowledge of the bank, so every correct answer has to come from retrieval, which makes groundedness straightforward to judge.

The corpus has 14 documents totaling about 24,200 words (roughly 48 pages at 500 words per page):

- a company profile and policy framework;
- 13 policies covering:
  - information security;
  - passwords and access control;
  - data protection;
  - ethics and conduct;
  - whistleblowing;
  - internal control;
  - KYC and KYCB;
  - branch operations;
  - leave and public holidays;
  - staff separation;
  - internal and corporate communication;
  - expenses and travel;
  - remote work.

These include the topics named in the project brief (PTO, security, expenses, remote work, holidays) alongside banking-specific policies.

Formats are mixed so that ingestion is tested on every required type: 8 Markdown, 2 HTML, 3 PDF, and 1 plain text. Every document carries a stable ID (for example VB-POL-006), a version, an effective date, and an owner. The metadata sits in YAML front matter, HTML meta tags, a PDF header table, or a plain-text header block, depending on format. Citations use these IDs.

Several features were built in to make evaluation meaningful:

- **Checkable facts:** policies state specific limits, deadlines, and retention periods rather than general principles.
- **Cross-references:** documents refer to each other. Mandatory block leave, for example, appears in the Internal Control, Leave, and Password policies, which supports multi-document questions.
- **Near misses:** some facts are deliberately close together, such as the 5-minute screen lock versus the 10-minute CoreLink session timeout, and the Fraud Desk versus the Speak Up Line. These test whether retrieval returns the right passage.
- **Superseded values:** revision histories record old values, such as the critical patch window reduced from 14 to 7 days. This tests whether the system reports the current rule.
- **Rules with exceptions:** for example, a public holiday that falls on a Saturday is observed the following Monday.

The corpus was frozen at the end of Stage 1 (git tag `corpus-v1`). Any later change requires the evaluation to be re-run.

## Success Metrics

Targets were set before any measurement.

| Metric | Type | What it measures | Target |
|---|---|---|---|
| Groundedness | Information quality | Share of answered in-scope questions whose content is fully supported by the retrieved chunks (LLM judge, validated against 10 hand-labeled answers) | 90% or more |
| Citation accuracy | Information quality | Share of answered in-scope questions where every citation points to a passage that supports its claim | 90% or more |
| Answer correctness | Information quality | Share of answers matching the gold answer fully or partially | 85% or more full or partial, 70% or more full |
| Refusal accuracy | Information quality | Out-of-scope questions refused, and in-scope questions wrongly refused | 100% refused; 5% or fewer false refusals |
| Retrieval hit rate | Information quality | Share of in-scope questions with a gold document in the top-k | 95% or more |
| Latency p50 / p95 | System | End-to-end time for `POST /chat` over 20 warm requests to the deployed app; cold start reported separately | p50 3 s or less, p95 6 s or less |
| Error rate | System | Non-200 or malformed responses during the evaluation run | 0% |
| Length compliance | System | Answers within the 200-word limit | 100% |

The evaluation set has 30 questions, the maximum the brief allows (it was planned at 25 and enlarged before any measurement, with the targets unchanged):

- 24 in scope, drawn from all 14 documents: 15 single-fact questions, 7 that need more than one document, and 2 about what changed between policy versions;
- 6 out of scope: general knowledge, another company's policy, two facts about the bank that the policies do not contain, a creative request, and a prompt-injection attempt.

With 24 in-scope questions, each is worth about 4.2 percentage points, so a 90% target allows at most two failures and the 5% false-refusal limit allows at most one.

## Ingestion Results

| Measure | Value |
|---|---|
| Documents | 14 (8 Markdown, 2 HTML, 3 PDF, 1 plain text) |
| Sections after parsing | 344 (including 14 generated "Document information" sections) |
| Chunks (heading strategy, 350 / 50) | 345 |
| Tokens per chunk | min 15, median 63, max 350 |
| Chunks with the window strategy (350 / 50) | 100, median 333 tokens |

Because almost every section is shorter than the chunk size, changing the chunk size barely affects the heading strategy. The chunking ablation therefore compares the two strategies (heading-aware sections versus fixed windows) rather than only varying the size.

## Relevance Threshold Calibration

Before choosing the gate threshold, ten questions were run against the index with the real embedding model, recording the best cosine similarity for each (vector search, top 1).

| Group | Question | Best similarity |
|---|---|---|
| Off topic | What is the capital of France? | 0.475 |
| Off topic | Write a poem about the ocean | 0.435 |
| Off topic | What is the current price of Bitcoin? | 0.586 |
| Off topic | How do I bake sourdough bread? | 0.437 |
| Sounds relevant, not covered | What is Veridane Bank's share price? | 0.761 |
| Sounds relevant, not covered | How much maternity leave do Google employees get? | 0.677 |
| In scope | Can I work from home three days a week? | 0.662 |
| In scope | Who do I call if my card is stolen? | 0.621 |
| In scope | How long do we keep CCTV footage? | 0.736 |
| In scope | What happens if I fail two phishing tests? | 0.631 |

The lowest in-scope score was 0.621, and three of the four off-topic questions scored below 0.48. A threshold of 0.55 blocks those three while leaving a margin of about 0.07 below the weakest in-scope question. The Bitcoin question (0.586) and both "sounds relevant" questions pass the gate, and must be refused by the prompt rule instead. The two "sounds relevant" questions score as high as real policy questions, which shows that a similarity threshold alone cannot enforce the corpus boundary. The evaluation set includes questions of both kinds so that each layer is measured.

## Deployment Notes

The free instance has 512 MB of memory and a tenth of a CPU. Measured locally with the production start command (gunicorn, one worker, two threads) and the offline stand-in embedder, the worker peaked at about 163 MB with Chroma, the index, and the web app loaded, and the gunicorn master used about 26 MB. Importing ONNX Runtime and fastembed adds about 70 MB before the bge-small model itself is loaded. `/health` reports the worker's peak memory (`peak_memory_mb`), which gives the real figure on Render: [add the value after the first deploy].

The first deploy exposed a start-up problem rather than a memory one. Render logged "HTTP health check failed (timed out after 5 seconds)" and restarted the instance, and a question asked at that time got a 502 error. Before the restart, `/health` showed the assistant never loading and memory stuck at the pre-load baseline, while after the restart the warm-up finished in 14.4 seconds. The warm-up thread had been started while the app module was still being imported, and loading the model inside a request could also tie up the server's two threads. The fix:

- start the warm-up from gunicorn's `post_worker_init` hook, after the app is fully imported;
- report its state and any error in `/health`, and write every thread's stack to the log if it stalls for 90 seconds;
- make `/chat` wait briefly for a running warm-up instead of loading a second copy of the model;
- compute the static parts of `/health` once at start-up;
- raise the server to four threads so the health check is never queued behind other requests.

## Evaluation Approach and Results

The evaluation code is in `evaluation/`, and every script adds its results to `evaluation/results/report.md`.

**Question set.** `evaluation/questions.jsonl` holds the 30 questions. Each in-scope question has a short reference answer written from the policy text and the list of documents that are acceptable sources for it.

**Answer quality** (`python -m evaluation.quality`). Every question goes through the same pipeline, settings, and index as the web app, run in-process so that the judge can see the full text of each excerpt the answering model saw. For each answer:

- automatic checks: whether an acceptable source reached the excerpts (retrieval hit), whether every cited document is an acceptable source, the length in words, and token F1 against the reference answer;
- an LLM judge, openai/gpt-oss-120b, which is larger than the answering model, openai/gpt-oss-20b. It decides whether every statement is supported by the excerpts (groundedness), whether each citation supports the statement it is attached to, and whether the answer matches the reference fully, partly, or not at all.

An answer counts toward citation accuracy only if the judge accepts its citations and every cited document is an acceptable source. Refused in-scope questions count as incorrect and are excluded from groundedness and citation accuracy, which are measured on answered questions; the false-refusal rate reports them separately.

**Judge validation** (`python -m evaluation.review`). Ten judged answers, chosen with the fixed seed, are labelled by hand without seeing the judge's verdicts, and the agreement on each of the three judgements is reported.

**Latency** (`python -m evaluation.latency`). The first 20 in-scope questions are sent to the deployed app's `/chat`, after the warm-up has finished, and each is timed from sending the request to receiving the full response. The first `/health` call is timed separately; if the service was asleep, it measures the wake-up.

**Rate limits.** Groq's free tier allows 8,000 tokens and 30 requests per minute for each model. The quality run tracks the tokens each request uses and waits when the next request would exceed a budget of 7,000 tokens per minute. The latency run spaces requests 20 seconds apart, because the deployed app uses the same account; a rate-limited request would measure the limit rather than the app. The two runs are not run at the same time.

**Iteration.** The first run met ten of eleven targets but gave only 62% fully correct answers. Its partial answers left out secondary details, and one answer was refused because it came back twice without valid citations. One general change followed: the "complete" answer style described under Design Decisions. It is not tailored to any evaluation question; the questions, reference answers, judge, and targets are unchanged. The first run is kept in `evaluation/results/runs/run1/`, the second run is compared with it side by side in the report, and the change can be reversed with `ANSWER_STYLE=concise`. The judge's hand-label check was made on the first run's answers and still applies, because the judge model and its instructions did not change.

**Retrieval ablations** (`python -m evaluation.ablation`). Six retrieval configurations are compared on the 24 in-scope questions without calling the LLM: hybrid versus vector-only search, heading-aware versus fixed-window chunking, and k of 3, 5, and 8. For each, the run reports the hit rate, the mean reciprocal rank of the first acceptable source, how many acceptable sources were retrieved, and how many questions fall below the relevance threshold. Answer quality is measured once, for the deployed settings, because a full quality run uses a large share of the free tier's daily token allowance.

### Results

Ten of the eleven targets were met. Full results, including every question, are in `evaluation/results/report.md`.

| Metric | Result | Target | Met |
|---|---|---|---|
| Groundedness (answered in-scope questions, n = 23) | 100% | ≥ 90% | Yes |
| Citation accuracy (n = 23) | 91% (21 of 23) | ≥ 90% | Yes |
| Correct, full or partial (n = 24) | 96% (23 of 24) | ≥ 85% | Yes |
| Correct, full (n = 24) | 62% (15 of 24) | ≥ 70% | No |
| Out-of-scope questions refused (n = 6) | 100% | 100% | Yes |
| In-scope questions wrongly refused (n = 24) | 4% (1 of 24) | ≤ 5% | Yes |
| Retrieval hit rate (n = 24) | 100% | ≥ 95% | Yes |
| Answers within 200 words (n = 23) | 100% | 100% | Yes |
| Failed requests (30 quality, 20 latency) | 0% | 0% | Yes |
| Latency p50 on the deployed app (n = 20) | 1.16 s | ≤ 3 s | Yes |
| Latency p95 on the deployed app (n = 20) | 1.93 s | ≤ 6 s | Yes |

**Correctness.** 23 of the 24 in-scope answers matched the reference answer fully or partly, but only 15 matched it fully, so the 70% target for full matches was missed. All eight partial answers were grounded and correctly cited. Each of their reference answers includes a secondary detail alongside the main fact, such as the 3 extra days of leave after 10 years of service (q01), the approvals needed for remote work (q07), or the ban on international transfers from Tier 2 wallets (q11). The judge's explanation for each verdict is in `evaluation/results/quality_results.json`. This is also the least reliable of the judge's verdicts: on the hand-labelled sample it agreed with the human labels 70% of the time, against 100% for groundedness. The target was not changed after the run.

**Refusals.** All six out-of-scope questions were refused:

- two by the relevance gate (the capital of France and the poem request);
- four by the model (another company's maternity leave, the bank's share price, the savings rate, and the prompt-injection attempt).

The highest out-of-scope similarity score (0.747) was above the lowest in-scope one (0.627). This confirms the calibration finding: no threshold separates the two groups, so the gate cheaply removes clearly unrelated questions and the prompt's refusal rule does the rest.

The one false refusal was q15 (who authorizes a USD 30,000 counter withdrawal). Retrieval found the right passages, but the model's answer came back twice without a valid citation, so the citation guardrail refused it rather than show an uncited answer.

**Citations.** 21 of 23 answers passed. Both failures were multi-document questions (q06 and q17), where the answer draws on several excerpts; in each, one citation was either judged not to support its statement or pointed to a document outside the acceptable list.

**Judge validation.** Ten judged answers were labelled by hand without seeing the judge's verdicts. The labels agreed with the judge on 100% of groundedness verdicts, 90% of citation verdicts, and 70% of correctness verdicts. The groundedness and citation figures can therefore be relied on; the full-versus-partial split less so. Mean token F1 against the reference answers was 0.51. Word overlap is only a rough check, because correct answers are often phrased differently from the reference.

**Latency.** On the deployed free instance, answers took 1.16 s at the median and 1.93 s at the 95th percentile (maximum 2.22 s). The server itself took 0.87 s at the median, so network and Render's proxy account for about 0.3 s. After a quiet period, the first request took 32.7 s to wake the service, and the model then takes about 15 s to load. So the first visitor after a quiet spell waits roughly 45 to 50 seconds, and later questions take about a second.

**Ablations.** Every configuration found an acceptable source for every in-scope question, so the differences are in ranking and coverage:

| Configuration | MRR | Source coverage | Out-of-scope questions gated |
|---|---|---|---|
| Heading chunks, hybrid, k = 5 (deployed) | 0.96 | 96% | 2 of 6 |
| Heading chunks, vector only, k = 5 | 0.93 | 93% | 2 of 6 |
| Heading chunks, hybrid, k = 3 | 0.96 | 93% | 2 of 6 |
| Heading chunks, hybrid, k = 8 | 0.96 | 96% | 2 of 6 |
| Window chunks, hybrid, k = 5 | 0.98 | 93% | 3 of 6 |
| Window chunks, vector only, k = 5 | 0.97 | 93% | 3 of 6 |

- **Hybrid versus vector only:** hybrid search ranked sources higher and covered more of them.
- **The value of k:** k = 3 lost coverage, and k = 8 added nothing over k = 5 while sending more tokens per request, which matters under an 8,000-token-per-minute limit.
- **Window versus heading chunks:** windows ranked the first source slightly higher but covered fewer sources. Each window is about five times longer than a heading chunk (median 333 tokens against 63), so citations would point to broader passages and each request would use more of the token limit.

The ablation therefore supports the deployed choice of heading chunks, hybrid search, and k = 5. No configuration gated an in-scope question.

**Limitations.** The set has 30 questions, answered once. The reference answers were written by the author of the corpus. A single judge model scored every answer, and its correctness verdicts are only moderately reliable. Latency was measured from one location in one session.
