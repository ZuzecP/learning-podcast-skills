# Markdown cards

Used when the config's `backend` is `markdown`. One Markdown file per podcast card, in the folder named by `cards_folder`. A relative `cards_folder` is resolved against the project folder; every call below gets the absolute path as `--folder`.

All reading and writing goes through `scripts/cards.py` (Python 3, standard library only). The skill's folder path contains a space: always quote the script path. Every call prints one JSON object. Success: exit 0 and `"ok": true`. Refusal: exit 2, `"ok": false`, and a `reason` to branch on, never the `detail` text.

```
python3 "<skill dir>/scripts/cards.py" name  --folder F --name "<title>"
python3 "<skill dir>/scripts/cards.py" write --folder F --card <card.json>
python3 "<skill dir>/scripts/cards.py" scan  --folder F
python3 "<skill dir>/scripts/cards.py" find  --folder F --query "<keywords>"
```

## Searching for earlier cards

`find` with the topic's main keywords. It matches any keyword, case-insensitive, in a card's name, theme, tags or summary, and returns the matches (name, theme, tags). You decide from the list whether the topic is already covered. It is a keyword match, not an AI search: try a synonym or two before concluding "first time".

## Name

Call `name` before the notebook is titled (`notebooklm.md`, step 3). Use the returned `stem` as the notebook title and the card Name, so the two never differ. If `exists` is true, append the format ("<stem> (Debate)") and call `name` again; if that exists too, append the creation date ("<stem> (Debate) 2026-11-09"). One source: its title without channel or site suffixes. Several sources or research: the topic in title case, at most 60 characters.

## Properties (frontmatter)

| Key | Value |
|---|---|
| `theme` | One theme. Choosable themes: the config's `themes` plus the themes `scan` returns. When several fit, the one for the main subject (what most of the summary is about), noted in the run notes. None fits: write a new free-text theme into the card and tell the user in the report. Never edit the config. |
| `tags` | 3 to 6 specific, lowercase. Reuse first: where a tag from `scan` fits, use it instead of a near-synonym. |
| `for` | `for_default` from the config unless the user said "for <name>". |
| `scenario` | Single, Multiple or Research |
| `source_types` | Podcast, Interview, Talk, Video, Article, Paper, Book, File, as a list: the content type plus the medium of every source that went in. |
| `format` | Deep Dive, Brief, Critique, Debate |
| `length` | Short, Default, Long; omit for Brief |
| `first_time_topic` | true or false (from `find`, never assumed) |
| `notebook` | The notebook URL; empty in fallback |
| `created` | The current date and time, ISO 8601 |

## The card file

Write a JSON file in the run's folder (`runs/`), not in `cards_folder`, with these keys, then call `write`:

- `name`: the `stem` from `name`
- the keys above: `theme`, `tags`, `for`, `scenario`, `source_types`, `format`, `length` (optional), `first_time_topic`, `notebook`, `created`
- `summary`: the NotebookLM summary verbatim; with two or more sources, the chat summary without its citation numbers
- `sources`: a list of objects with `title` (the paper's or page's real title, not NotebookLM's raw one), `url`, `type`, `origin`, `in_out`, `reason`. Origin: You (the user's links), Claude (your picks, swaps and alternatives), NotebookLM (Deep Research), Both. Every unticked source is a row with `in_out` Out and the reason. A swap is two rows: the user's original Out, the replacement In.
- `prompt`: the instruction block, verbatim
- `run_notes`: a list of lines (cuts, Spotify swaps, Generate later, fallback, resumed; leave the list empty when nothing happened)

The script writes the frontmatter and the four sections (Summary, Sources, Prompt used, Run notes) itself, escapes the table, and never overwrites a file.

## Refusals

| `reason` | Do |
|---|---|
| `exists` | Apply the Name rule above (format, then date) and write again. |
| `no_folder`, `outside_folder`, `bad_input` | Stop and tell the user which; fix a malformed card file once if the cause is yours. |
| `io_error` | Retry once; else set `card_pending: true` with the card in the state file and show the card in chat (`failures.md`). |
