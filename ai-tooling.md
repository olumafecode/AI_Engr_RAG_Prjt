# AI Tooling

This file records which AI tools were used on the project, how they were used, and what worked and what didn't. Edit the bracketed prompts so they reflect your own experience.

## Stage 0: Repository and environment

**Tool:** Claude (claude.ai chat)

**How I used it:** I asked Claude to generate the project skeleton: the Flask app factory and routes, settings, pinned requirements, the pytest suite, the GitHub Actions workflow, VS Code settings, and the README. Claude ran the tests and the linter before handing the files over.

**What worked well:** [e.g. the workflow and tests passed on the first push]

**What I had to check or fix:** [e.g. anything that needed changing on your machine or in GitHub]

## Stage 1: Corpus and success metrics

**Tool:** Claude (claude.ai chat)

**How I used it:** I chose the domain (a bank) and the policy topics, and Claude drafted a fictional company profile and 13 policies in the formats I needed (Markdown, HTML, plain text, and Markdown sources for the PDFs). I reviewed each batch and directed changes. These included adding Digital Financial Services as a fifth business segment with five business heads, adding the CIO/CTO role, and adding DFS support and fraud reporting contacts. Claude tracked facts shared across documents so later drafts stayed consistent with earlier ones, and wrote the script that renders the PDFs.

**What worked well:** [e.g. drafting in batches of three made review manageable; cross-references between policies gave me multi-document evaluation questions for free]

**What I had to check or fix:** [e.g. which roles owned which policies; consistency of limits and deadlines across documents]


## Stage 2: Ingestion and indexing

**Tool:** Claude (claude.ai chat)

**How I used it:** Claude wrote the parsers for each format, the chunking module, the embedding and Chroma wrappers, the ingestion and search commands, and tests that run without downloading the model. I installed the update, built the index locally, checked search results, and pushed.

**What worked well:** [e.g. the retrieval smoke test in CI confirmed the index works end to end]

**What I had to check or fix:** [e.g. refreshing .env after the chunk settings changed]


## Stage 3: Retrieval and generation

**Tool:** Claude (claude.ai chat)

**How I used it:** I ran calibration questions against the real index and shared the similarity scores, and Claude used them to set the relevance threshold (0.55) and to add keyword search (BM25) alongside vector search. Claude wrote the prompt, the Groq client, the citation and length checks, the /chat and /docs routes, and tests that use a scripted stand-in for the LLM. I tested each change live and reported the results.

**What worked well:** Measuring before deciding. The calibration scores showed that tricky questions (another company's maternity leave, the bank's share price) score as high as real questions, which is why refusal is handled both by a threshold and by the prompt.

**What didn't work at first:**
- The suggested model, llama-3.1-8b-instant, had been retired by Groq, and the first live request failed with `model_not_found`. We switched to Groq's recommended replacement, openai/gpt-oss-20b. Because it is a reasoning model, it needed low reasoning effort and a larger token budget so the answer isn't cut off.
- The model bolded answers with Markdown, which the chat page displays as raw asterisks. The prompt now asks for plain text, and the code strips any bold.
- "What changed in the password policy?" was refused. Printing the retrieved excerpts showed the Revision History never reached the model, so the refusal was correct given its evidence. A retrieval rule now adds the Revision History for questions about changes.