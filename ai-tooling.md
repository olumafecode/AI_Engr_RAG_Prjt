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

## Stage 4: Web application

**Tool:** Claude (claude.ai chat)

**How I used it:** Most of the web layer was built alongside Stage 3. Claude wrote the Flask routes: the chat page (`/`), the chat API (`/chat`), the health check (`/health`), and a source view (`/docs/<doc ID>`) that opens each document at the cited section, or at the cited page for PDFs. It also turned the Stage 0 placeholder page into a working chat page that shows numbered citations with snippets and links. I tested the page in the browser and reported what I saw.

**What worked well:** Designing the `/chat` response format early (answer, citations, snippets, links, timings) meant the page, the command-line tool, and the tests all used the same contract. Linking each citation to the exact section made answers easy to check by hand.

**What didn't work at first:** The model's Markdown bold showed up as raw asterisks on the page, because the page displays plain text. The fix went into the prompt and a code clean-up step (see Stage 3).

**What I had to check or fix:** [e.g. whether source links opened at the right section in each format]

## Stage 5: Deployment and CI/CD

**Tool:** Claude (claude.ai chat)

**How I used it:** Claude checked Render's current documentation before writing the deployment set-up. The free tier still exists, with 512 MB of memory, a tenth of a CPU, sleep after 15 minutes idle, and 750 free hours a month per workspace. Claude then wrote `render.yaml`:

- the vector index is built during Render's build step, because the running service's files are not kept;
- one gunicorn worker keeps memory low;
- the Groq key is entered in Render as a secret rather than stored in the repository;
- Render's auto-deploy is off, so deploys come only from the GitHub Actions deploy hook after tests pass.

It also added a background warm-up at start-up and a peak-memory figure in `/health`. I created the service from the Blueprint, added the deploy hook as a GitHub secret, and confirmed a push to `main` deployed automatically.

**What worked well:** Checking the documentation first caught two things that would have caused problems:

- a Blueprint without an explicit plan gets a paid plan;
- Render's default Python (3.14) is newer than some of our libraries support, so the version is pinned to 3.12.11.

Measuring memory locally before deploying gave a baseline to compare with Render's real figure.

**What didn't work at first:** **What didn't work at first:** On the first deploy the model never finished loading: `/health` showed memory stuck at 88 MB. When I asked a question, Render's health check timed out, it restarted the instance, and the question failed with a 502 error. After a restart the model loaded fine, which pointed to a timing problem rather than memory. The warm-up thread was being started while the app was still being imported, and loading the model inside a request could tie up the server's two threads. Claude moved the warm-up to gunicorn's `post_worker_init` hook, added the warm-up state and any error to `/health`, made questions wait briefly instead of loading a second copy of the model, and raised the server to four threads. After that, every start loaded the model in about 15 seconds.

**Deployment results:** First build took 2 minutes. Peak memory on Render was 341 MB of 512 MB. The model loaded in 14.6 seconds at start-up, and a warm answer took 0.8 seconds. Waking from sleep took about [X] seconds. However, after the fix deployment took 16 minutes

**Deployment results:** First build took [X] minutes. Peak memory on Render was [X] MB of 512 MB. Cold start after sleeping took about [X] seconds, and warm answers took about [X] seconds.

## Stage 6: Evaluation

**Tool:** Claude (claude.ai chat)

## Stage 6: Evaluation

**Tool:** Claude (claude.ai chat)

**How I used it:** Claude wrote the 30-question evaluation set, with reference answers checked against the policy text, and the evaluation scripts: an in-process quality run judged by openai/gpt-oss-120b, a latency run against the deployed app, retrieval ablations, and a blind hand-labelling tool to validate the judge. I ran each script, hand-labelled 10 answers, and shared the report.

**What worked well:** Pacing the requests to Groq's free-tier limits meant every run finished with no failed requests. Saving progress after every question meant an interrupted run could resume. Fixing the targets in Stage 1 kept the evaluation honest: the first run missed one target (fully correct answers, 62% against 70%), and we reported it rather than adjusting it.

**Iteration:** We then tried one general prompt change, asking for every condition and contact that the excerpts attach to the answer. It raised fully correct answers to 92%, but citation accuracy fell to 75%. The answer characteristics showed why: answers were 72% longer while citing the same number of documents. Because citation accuracy is a required metric, we kept the original prompt for deployment and reported the second run as a prompt-variant comparison. Keeping the first run's exact wording as a named option, checked by a test, made switching back a one-line change.

**What didn't work as hoped:** The judge's full-versus-partial verdicts agreed with my labels only 70% of the time, so that metric is the least reliable.