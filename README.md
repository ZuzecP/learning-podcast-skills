# learning-podcast-skills

[![tests](https://github.com/ZuzecP/learning-podcast-skills/actions/workflows/test.yml/badge.svg)](https://github.com/ZuzecP/learning-podcast-skills/actions/workflows/test.yml)

Claude Code skills that turn a link, several links or a topic into a NotebookLM (Gemini Notebook) Audio Overview built to fixed listening rules, and file a card for it in a Notion database.

- `learning-podcast-setup`: guided first-time setup.
- `learning-podcast`: runs the whole flow in the Claude app's built-in browser and writes the Notion card.
- `podcast-prompt`: builds the Audio Overview instructions from a rules file.

Version 1.0 stores cards in Notion only. See `CHANGELOG.md`.

## Prerequisites

- The Claude desktop app with the Code tab and its built-in browser. The flow drives NotebookLM there.
- A Notion connector with write access.
- A Google account signed in to NotebookLM in the built-in browser.
- Anthropic's `deep-research` and `built-in-browser` skills. Research runs need the first; the setup checks for both and reports what is missing.
- Python 3 (standard library only) for the helper scripts.
- macOS. It is the only platform the author uses; others are untested.

## Install

```bash
git clone https://github.com/ZuzecP/learning-podcast-skills.git
sh learning-podcast-skills/scripts/install.sh "/path/to/your/project folder"
```

This links the three skills into the project folder's `.claude/skills/`. Start Claude Code sessions in that folder. Running it again is safe; `--force` repoints a link that points elsewhere. It refuses to touch a real file or folder.

## Set up

Open Claude Code on the project folder and say "set up learning podcast". The setup:

1. Reports which prerequisites it found.
2. Asks four questions, one at a time, each with a default: language (English), who the cards are for (`Me`), the starter themes, and the optional NAMES rule (off).
3. Creates the Notion "Podcasts" database after telling you exactly what it will create, or adopts an existing database whose URL you paste after checking its properties.
4. Writes `learning-podcast.config.json` in the project folder.

## Use

Paste a link, several links, file paths or a topic. Optional: a format (Deep Dive is the default; Brief, Critique, Debate), a length, "for <name>", or "dry run" (builds the prompt and the card content without touching NotebookLM or Notion).

A topic runs the `deep-research` skill first and asks you scope questions. The run does not wait for the audio: generation finishes in NotebookLM, and the Notion card holds the sources and the exact prompt used. An interrupted run resumes when you send the same request again; each run keeps a state file in `runs/`.

## Configuration

`learning-podcast.config.json` lives in the project folder and is never committed. `config.example.json` shows the keys.

| Key | Meaning | Default |
|---|---|---|
| `data_source_id`, `database_url` | Your Notion database | written by the setup |
| `for_default` | Default value of the card's `For` property | `Me` |
| `language` | Audio Overview language, chosen in NotebookLM's "Choose language" list | `English` |
| `names_rule` | Add the Czech-names line to the prompt (see `rules.md`) | `false` |
| `rules_file` | Path to your own rules file | `null` |
| `setup_completed` | Set by the setup; the run refuses to start without it | |

**Language.** To change it, edit `language` in the config. If NotebookLM's list does not offer it, English is used and the run tells you. Audio in languages other than English is untested, and the instruction block stays in English.

**Rules.** The wording of the instructions lives in `skills/podcast-prompt/references/rules.md`, with a line on why each rule exists. Copy it to `rules.local.md` in your project folder, edit the copy, and set `rules_file`; the copy replaces the shipped file as a whole.

**Themes and tags.** Read from the live Notion schema on every run. If no theme fits, the run adds one and tells you.

## Tested and not tested

Tested: a single YouTube source and a research run with ten papers (author's runs, October 2026); the helper scripts and file layout (`python3 -m unittest discover -s tests -v`); the config gate and the setup skill as scenario exercises (`docs/measured-facts.md`).

Not tested: re-running a finished request, resuming an interrupted research run, local and Google Drive files, Spotify links, non-English audio, whether an unticked source stays out of the audio, and the setup on an account other than the author's.

## Limitations

- It drives the NotebookLM web app through the built-in browser. That is unofficial, and a UI change can break a step; the skill then falls back to a package you paste by hand. Dated UI notes are in `skills/learning-podcast/references/notebooklm.md`.
- It acts in your signed-in Google account. Check that automated use fits the terms of your Google account.
- Notion is the only storage backend in this version.
- The instruction box limit (5,000 characters) and the length options were measured in October 2026 and can change.
- This is not an official Google, Notion or Anthropic project.

## License / usage terms

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/): free to share and adapt with attribution to Zuzana Pešková, not for commercial use. See `LICENSE`.

## Contributing

See `CONTRIBUTING.md`. Run `python3 -m unittest discover -s tests -v` and `sh scripts/check-public.sh` before you push.
