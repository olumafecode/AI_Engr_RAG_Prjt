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
