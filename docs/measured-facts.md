# Measured facts

Facts about NotebookLM measured while building the skills. They can change; each carries its date. UI observations are in `skills/learning-podcast/references/notebooklm.md`.

## NotebookLM (October 2026)

- The Audio Overview "Customise" dialog's focus box is a textarea with `maxlength` 5000 (measured 2026-10-06). The prompt is cut in a fixed order when it would exceed the limit.
- Length options per format: Deep Dive offers Short, Default and Long; Critique and Debate offer Short and Default; Brief has no length setting.
- Clicking the Studio "Audio Overview" tile opens the Customise dialog; it does not generate.
- Length rule used by `length.py`: one source is Long at 60 minutes for a conversation, 30 minutes for a talk, 3,000 words for written text; several sources are always Long; Long exists only for Deep Dive.

## Scenario exercise: config and run gate (2026-11-08)
Baseline on the skill without the gate: (a) no config: starts the run; (b) example config copied: starts the run, placeholder IDs would fail only at the card step after the audio exists; (c) Notion data source unreachable: carries on with NotebookLM and falls back to card_pending; (d) unsupported language: falls back to English and tells the user (language hardcoded).
After the edit: (a) stops and runs setup; (b) rejects the template config, stops, touches neither NotebookLM nor Notion; (c) stops at the start, tells the user which source is unreachable, writes nothing; (d) English fallback, told in the report and the run notes, now driven by the config's language.

## Scenario exercise: setup skill (2026-11-08)
Baseline without the skill: S1 (fresh user) asked all questions at once and created the database after one round, with no stated list and no explicit yes; S2 (deep-research missing) gave no prerequisite report and mentioned the missing skill only at the end; S3 (adopting a database lacking the Debate option) asked before adding it (correct); S4 (board view fails) kept the database, retried once and gave manual steps (correct).
With the skill: S1 reports prerequisites first, asks the four defaults one at a time, lists exactly what will be created and waits for a yes before creating; S2 reports the missing skill at the start and carries on; S3 adds Debate only after a yes and creates no second database; S4 keeps the database, retries once, gives two manual steps and still writes the config.
