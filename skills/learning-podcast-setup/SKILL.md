---
name: learning-podcast-setup
description: Use when the user asks to set up learning podcast, or when learning-podcast finds its config missing, incomplete or holding REPLACE-ME.
---

# Learning podcast setup

Writes `learning-podcast.config.json` in the project folder and, with the user's yes, creates or adopts the card store: the Notion "Podcasts" database, or a local folder of Markdown files. Every setting is a default the user confirms or changes.

## 1. Backend

Ask first, before anything else: "Do the cards go to Notion or to a local folder of Markdown files?" The answer sets `backend` (`notion` or `markdown`) and decides which steps below apply.

## 2. Prerequisites

Check this session's tools and skills and report each as found or missing, one line each:

| Needed | If missing |
|---|---|
| Built-in browser tools (`mcp__Claude_Browser__*`) | Stop; say how to enable them |
| Notion connector with write access (Notion backend only; skip it for Markdown) | Stop; say how to connect it |
| `anthropic-skills:built-in-browser` skill | Say so; carry on |
| `anthropic-skills:deep-research` skill | Say research runs are unavailable; carry on |

NotebookLM sign-in is checked at the first run (`learning-podcast/references/notebooklm.md`, step 2), not here.

## 3. Defaults, one question at a time

Ask each as its own message and wait for the answer:

1. "The default language is English, keep it?" If not: which language? It must be in NotebookLM's "Choose language" list, and not every language is supported; it is checked against that list at the first run, with English as the fallback.
2. "Cards are for `Me` by default (`for_default`), keep it?"
3. "The starter themes are People & Culture, Leadership & Communication, AI & Technology, Career, Data & Analytics, Garden & Plants, Home & Cooking, 3D Printing and Personal Development, keep it?" The user may add, remove or rename. Tags start empty.
4. "The NAMES rule (for Czech names with diacritics) is off, keep it?"

## 4. Notion

Only when the backend is Notion. Ask: create a new database, or adopt an existing one (paste its URL)?

**Create.** Ask for the parent page, or offer a private draft. Then say exactly what will be created and wait for a yes: database "Podcasts" with Name (title), Theme (select, the confirmed themes), Tags (multi-select, empty), For (select, the default), Scenario (Single, Multiple, Research), Source types (multi-select: Podcast, Interview, Talk, Video, Article, Paper, Book, File), Format (Deep Dive, Brief, Critique, Debate), Length (Short, Default, Long), First-time topic (checkbox), Notebook (URL), Created (created time); views "By theme" (board grouped by Theme) and "All" (table, newest first). After the yes, create it and fetch the data source to verify. If a view cannot be created, keep the database, retry once, tell the user, and give two manual steps: add a Board view grouped by Theme; add a Table view sorted by Created, newest first. The views are optional; the properties are not.

**Adopt.** Fetch the URL. Pass means every property above exists with the right type and the fixed option sets (Scenario, Format, Length, Source types) are present; Theme, Tags and For are free-form. List any missing options and add them only after a yes; if anything else is missing, refuse with the list and create nothing. Never create a second database.

## 5. Markdown folder

Only when the backend is Markdown. Ask for the folder that will hold the cards (default: `podcasts/` in the project folder). Show its absolute path and say it will be created if it does not exist; wait for a yes. Then create it with `mkdir -p` and check with a shell test that it is writable. An existing folder is adopted as it is: nothing in it is read, changed or moved. A folder has no schema, so there is nothing else to verify; the themes live in the config and in the cards.

## 6. Write the config

Write `learning-podcast.config.json` with the keys of `config.example.json`, the confirmed answers, `rules_file` null, and `"setup_completed": true`.

- Notion: `"backend": "notion"`, the verified data source ID and database URL; `cards_folder` null and `themes` empty.
- Markdown: `"backend": "markdown"`, `cards_folder` as the user gave it, `themes` as the confirmed list; leave `data_source_id` and `database_url` out.

Show it. Tell the user that to change the instruction wording they copy `rules.md` to `rules.local.md` and set `rules_file`. Suggest a dry run: "dry run" plus a link.

## Never

- Create or change anything in Notion, or create the cards folder, before the yes.
- Write a config that still holds `REPLACE-ME` in a key its backend uses, or (Notion) before the data source fetch has succeeded, or (Markdown) before the folder exists and is writable.
- Ask the user for tokens or passwords.
