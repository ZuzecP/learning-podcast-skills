# Run state and resume

One JSON file per run: `runs/<YYYY-MM-DD>-<slug>.json` in the project folder (slug: up to 6 lowercase title words joined by hyphens). Create it when step 2 ends (Research: once the user has answered the scope questions; until the title exists, the slug uses the topic's words) and rewrite it with the Write tool after every later step. A dry run writes no state file.

## Fields

- `request`: the user's message, verbatim
- `key`: the format plus the sorted list of the user's source URLs and file paths; for Research, the format plus the topic as the user wrote it, in lowercase, plus the user's seed URLs. The same link with another format, or a reworded topic, is a new run.
- `title`, `scenario`, `format`, `length`, `first_time`
- `scope`: Research only, the user's answers to the scope questions; `question`: the scoped research question, as given to both lists
- `sources`: one entry per source: title, url or path, kind, size (only for sources that go in; null otherwise), card source type, origin (You = the user's links, Claude, NotebookLM, Both), in or out, reason
- `notebook_url`, `prompt`, `run_notes`
- `done`: the steps finished, with 3a, 3b and 3c as separate entries
- `card_url`; or `card_pending: true` plus `card` (properties and body) when the card write failed

## At intake (step 0)

1. List `runs/`. Any file with `card_pending: true`: write that card first (step 8), then carry on.
2. A file whose `key` matches this request is an interrupted run. Continue from the first step not in `done`, reusing its title, sources and prompt; don't regenerate them, and add "resumed" to the run notes.
3. Before adding anything to a reopened notebook, compare its Sources panel with `sources`: add only what is missing. Check Studio for an audio from this run before generating again.
4. Every step in `done`: report the run as done, with the card link, and change nothing.
