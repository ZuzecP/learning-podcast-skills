# Changelog

## v2.0 (2026-11-09)

Cards can be stored in a local folder of Markdown files instead of Notion.

### Added
- A Markdown card store: one `.md` file per card, properties as YAML frontmatter, the same four body sections as the Notion card. `skills/learning-podcast/scripts/cards.py` writes the files (never overwriting), scans the folder for themes and tags, and finds earlier cards by keyword. Reference: `skills/learning-podcast/references/markdown.md`.
- Config keys `backend` (`notion` or `markdown`), `cards_folder` and `themes`.
- `learning-podcast-setup` asks first whether cards go to Notion or to a local folder.

### Changed
- The README no longer lists a platform prerequisite or a "tested" chapter, and words the pre-pull-request check as a step before opening one.
- Tests that asserted on documentation wording were removed; the code tests stay.

### Compatibility
- A v1.0 config without `backend` runs as Notion, unchanged.

## v1.0 (2026-11-09)

First public version. Storage is Notion only.

### Added
- `learning-podcast`: turns a link, several links or a topic into a NotebookLM Audio Overview in the built-in browser and files a card in a Notion database. Research runs use the `deep-research` skill and NotebookLM's Deep Research, with a cross-check table. Interrupted runs resume from a state file.
- `podcast-prompt`: builds the instruction block from `rules.md`; `--rules` points it at your own file.
- `learning-podcast-setup`: guided setup with opt-out defaults (language, `For`, starter themes, NAMES rule); creates or adopts the Notion database after confirmation; writes the config.
- `learning-podcast.config.json` and a run gate: the run stops when the config is missing, incomplete, holds `REPLACE-ME`, or the Notion data source is unreachable.
- The Czech-names rule as an optional locale rule (`names_rule`, off by default).
- `scripts/install.sh`, `scripts/check-public.sh`, unit tests on synthetic fixtures, and CI.
- Documentation: `docs/how-it-works.md`, `docs/measured-facts.md`.

### Known issues
- In a new database the Tags property has no options, so the first card is rejected until the options are added; the skill then adds them and retries.
- `references/notion.md` names the Notion Markdown spec as `notion://docs/enhanced-markdown-spec`; it now resolves to the renamed `notion-flavored-markdown-spec`.
