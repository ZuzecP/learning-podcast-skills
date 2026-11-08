# How it works

`learning-podcast` follows ten steps. The full procedure is in `skills/learning-podcast/SKILL.md`; this is the short version.

0. **Intake.** Config gate, then look for an interrupted run in `runs/` and resume it.
1. **Scenario.** Single source, Multiple sources, or Research (a topic).
2. **Sources.** Title, address, kind, size and people for each source; unreadable pages are swapped for an open copy.
3. **Research** (topic requests only). The `deep-research` skill builds a shortlist; NotebookLM's Deep Research builds another; a cross-check table decides what goes in.
4. **Notebook.** Create or reopen the notebook, add sources, check every source title, untick failed ones (never delete).
5. **Summary.** One source: NotebookLM's summary. Several: a summary written from NotebookLM's chat.
6. **Prompt.** `podcast-prompt` assembles the instruction block from the rules file.
7. **Generate.** Length from `length.py`, language from the config, then Generate.
8. **Card.** Every property and body section in Notion, including the exact prompt used.
9. **Report.** A few lines: what was made, what was dropped or swapped, the Notion link.

Two scripts hold the deterministic parts: `skills/learning-podcast/scripts/length.py` (length rule) and `skills/podcast-prompt/scripts/assemble.py` (prompt assembly with a fixed cut order when the block exceeds the box limit).
