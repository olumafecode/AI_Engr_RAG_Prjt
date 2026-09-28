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
| Prompt format | System rules, then excerpts labeled [S1] to [S5] with doc ID, title, version, and section, then the question | Short labels are easy for the model to cite and easy for code to check. The rules require a citation on every sentence, an answer whenever any excerpt contains the information, the exact refusal sentence only when none does or the question concerns another organization, the current rule unless the question asks what changed (Revision History excerpts answer those), plain text without Markdown, and at most 200 words. The first live run with gpt-oss-20b refused "What changed in the latest version of the password policy?" even though the revision history is ranked in the top five, and bolded one answer; the rules for answering, revision history, and plain text were made explicit after that run. The next run showed the real cause: the revision history was not among the five excerpts, so the refusal was correct behaviour for the evidence the model had. Questions about changes match a policy's topic more closely than its terse version notes, so a retrieval rule now adds the top-ranked document's Revision History chunk as a sixth excerpt whenever the question asks about changes, updates, or earlier values. `python -m app.ask` marks such excerpts as added. Instructions inside excerpts or questions are to be ignored. |
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

The evaluation set has 25 questions:

- 20 in scope, spread across all 14 documents, with about 4 needing more than one document;
- 5 out of scope.

With 20 in-scope questions, each question is worth 5 percentage points.

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

The free instance has 512 MB of memory and a tenth of a CPU. Measured locally with the production start command (gunicorn, one worker, two threads) and the offline stand-in embedder, the worker peaked at about 163 MB with Chroma, the index, and the web app loaded, and the gunicorn master used about 26 MB. Importing ONNX Runtime and fastembed adds about 70 MB before the bge-small model itself is loaded. `/health` reports the worker's peak memory (`peak_memory_mb`), which gives the real figure on Render: 340 MB once the model had loaded and 341 MB after answering a question, about two-thirds of the limit. On Render the warm-up took 14.6 seconds, and a warm question was answered end to end in about 0.8 seconds..

The first deploy exposed a start-up problem rather than a memory one. Render logged "HTTP health check failed (timed out after 5 seconds)" and restarted the instance, and a question asked at that time got a 502 error. Before the restart, `/health` showed the assistant never loading and memory stuck at the pre-load baseline, while after the restart the warm-up finished in 14.4 seconds. The warm-up thread had been started while the app module was still being imported, and loading the model inside a request could also tie up the server's two threads. The fix:

- start the warm-up from gunicorn's `post_worker_init` hook, after the app is fully imported;
- report its state and any error in `/health`, and write every thread's stack to the log if it stalls for 90 seconds;
- make `/chat` wait briefly for a running warm-up instead of loading a second copy of the model;
- compute the static parts of `/health` once at start-up;
- raise the server to four threads so the health check is never queued behind other requests.

## Evaluation Approach and Results

To be completed in Stage 6. The planned approach:

- Run the 25-question set against the deployed app.
- Score groundedness and citation accuracy with a larger judge model than the one that generates answers.
- Validate the judge against 10 hand-labeled answers.
- Time every request.
- Run an ablation over k and chunk size.
