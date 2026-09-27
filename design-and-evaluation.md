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

Question answering (per request; Stage 3)
  POST /chat {"question": ...}
    -> embed the question
    -> retrieve top-k chunks from Chroma (optional rerank)
    -> relevance gate: refuse if nothing is similar enough
    -> build prompt with labeled sources
    -> LLM (Groq, llama-3.1-8b-instant, temperature 0, capped length)
    -> check citations against the retrieved chunks
    -> JSON: answer, citations (doc ID, title, section, snippet, link), latency
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
| Retrieval | Top-k with k = 5 | Covers questions that need two documents without flooding the prompt. Confirmed or changed by the ablation in the evaluation. |
| LLM | Groq free tier, llama-3.1-8b-instant | Very low latency helps the latency metric. The OpenAI-compatible API means OpenRouter can be swapped in through configuration. |
| Prompt format | System rules, then numbered context blocks labeled with doc ID and section, then the question | Labeled blocks make it easy for the model to cite, and easy for code to check the citations. |
| Guardrails | Similarity threshold before the LLM call, prompt-level refusal rule, token cap, and post-generation citation check | Refusal and citation rules are enforced in code as well as in the prompt, so they do not depend on the model alone. |
| Hosting | Render free web service | Named in the brief. Deploys are triggered by CI only after tests pass. |
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

## Evaluation Approach and Results

To be completed in Stage 6. The planned approach:

- Run the 25-question set against the deployed app.
- Score groundedness and citation accuracy with a larger judge model than the one that generates answers.
- Validate the judge against 10 hand-labeled answers.
- Time every request.
- Run an ablation over k and chunk size.
