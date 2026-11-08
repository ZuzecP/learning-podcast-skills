---
name: podcast-prompt
description: Use when writing the custom instructions for a NotebookLM (Gemini Notebook) Audio Overview for the user from a notebook summary, its sources and the chosen format. Called by learning-podcast at step 6, or on its own when the user builds a notebook by hand and wants the prompt.
---

# Podcast prompt

Builds the Audio Overview instruction block. `scripts/assemble.py` copies the texts from `references/rules.md` verbatim; your part is deciding whether the names line and the study tips apply. Text in, text out: no browser, no Notion. The skill's folder path contains a space: always quote script paths.

## Inputs

- summary: NotebookLM's notebook summary (or one the user pastes)
- sources: title and kind of each source
- people: full names of hosts, guests and authors as the sources write them, from the summary, the source titles or the video page
- format: Deep Dive (default), Brief, Critique or Debate
- first_time: true when no earlier Notion card covers the topic
- config: `names_rule` and `rules_file` from `learning-podcast.config.json`

## Steps

1. Names: only when the config's `names_rule` is true, pass `--names` when any person in `people` has a Czech name with special characters of the Czech alphabet in their first name, their surname or both. Judge whether the name is Czech; there is no letter list. An accented French, Spanish or Scandinavian name doesn't count. The NAMES line states the rule; the hosts pick the name themselves.
2. Build:
   `python3 "<skill dir>/scripts/assemble.py" --format "<format>" [--names] [--first-time] [--rules "<rules_file>"]`
   The block goes to stdout; a `notes:` line (characters, cuts) goes to stderr. Pass `--rules` only when `rules_file` is set in the config (the file replaces `rules.md` as a whole). The limit comes from the rules file in use; pass `--limit <n>` only when learning-podcast measured a different one.
3. Exit code 2 ("too long even after all cuts"): stop and tell the user, with the character count. Never shorten the block by hand.
4. Output: the block verbatim in a code block, then one run-notes line: cuts, or "none". Wording changes go into `rules.md`, never into a generated block. A request about the episode itself (shorter, less rambling) is a format or length choice: suggest Brief or a shorter length, not a trimmed block.

The prompt carries no listener profile: never add facts about the user to the block.
