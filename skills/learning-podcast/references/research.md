# Research (step 3)

## a. Your shortlist: the deep-research skill

A research request always runs **anthropic-skills:deep-research** on the user's topic. First, its step 1 every time, not only "if necessary": ask the user the scope questions (at least one: angle or lens, what is in and out), as open questions in chat, not an option box. Wait for the user's answers, write them to the state file's `scope`, and write one scoped question (the user's topic plus their answers, one or two sentences) to `question`; both lists (a. and b.) get exactly that text. On a resumed run with `scope` filled, don't ask again.

Two additions to how the skill runs:
- Pass `model: "sonnet"` on every researcher and on the report writer it spawns (the user's usage limit).
- Add to each researcher's objective: "List 2 to 4 primary sources with full text open without a login, each with URL, authors, year and one line on what it adds. Prefer arXiv or ar5iv, the author's or lab's own copy, or an open-access journal; no PubMed Central, no ResearchGate."

Its researchers run in the foreground: nothing else happens until they finish. They write their notes to the project folder's `research_notes/<title>/`, and its report writer writes the report to `reports/`; the report goes to the user as that skill says, and its path goes in the run notes. On a resumed run, read the existing notes instead of running the researchers again. From the researchers' notes, shortlist up to 10 sources including the user's seeds, one-line reason each, and write them to the state file.

## b. NotebookLM's list

Create the notebook and run Deep Research on the same question (`notebooklm.md` steps 1 to 4). To overlap the two, do b. first: create the notebook, submit Deep Research, then run a. while NotebookLM works. Open its results only once a.'s shortlist is in the state file. If a. ends after that point and results are there, use them. No results 10 minutes after submitting: use your shortlist alone.

## c. Cross-check

Overlap first, then fill gaps from either list. Write every Deep Research result and every pick of yours to the state file (origin, in or out, reason) before importing: NotebookLM discards what isn't imported.

| Item | In or out |
|---|---|
| NotebookLM's Deep Research report (its own checkbox at the top of the list) | Out: NotebookLM's own summary, not a source; on 2026-10-24 its figures differed from the papers |
| A paper already in, in another copy | Out: each paper counts once, whatever the site |
| ResearchGate page | Out. Look for the paper's open copy (WebSearch, WebFetch); none: Out, and tell the user (they can request it with their own account) |
| PubMed Central or academic.oup.com page | Out; use the arXiv, ar5iv or author copy (both failed on 2026-10-24, `notebooklm.md` Limits) |
| Vendor or marketing page | Out |
| Blog without data of its own | Out |
| Primary source with open full text | In, up to 10 in total |

More than 10: keep the overlap first, then the sources closest to the user's question. Fewer than 10 good sources: import fewer. Never fill the count with Out items.

arXiv: paste the HTML version (`arxiv.org/html/<id>`) or ar5iv (`ar5iv.labs.arxiv.org/html/<id>`), not the abstract page. A PDF URL works but imports with the URL as its title (step 5 renames it).

## A pick that fails to import

One other open copy of the same work (same title and authors), then the next In-worthy candidate in the state file, else continue with fewer. Never open the failing page in the built-in browser; check the alternative with WebFetch. This holds for the user's links too: their seed is the paper, not the site, so a failing seed is swapped for its open copy (two rows in the ledger, as for a Spotify swap).
