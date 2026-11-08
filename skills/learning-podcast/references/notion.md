# Notion: Podcasts database

- Data source: `data_source_id` in `learning-podcast.config.json` (use it as data_source_id when creating cards, and as `collection://<data_source_id>` when searching). The database address is `database_url`.
- Views: "By theme" (board grouped by Theme, cards show Name, Tags, Format; empty themes are hidden), "All" (table, newest first: Name, Theme, Tags, Format, Created). Other properties show only on the card.

Before writing card content in a session, `notion-fetch` `notion://docs/enhanced-markdown-spec` (the tool requires it).

## Searching for earlier cards

`notion-search` with `query` = the topic's main keywords and `data_source_url` = the data source above. It uses AI search by itself when the workspace has it (checked 2026-10-12: there is no separate AI-search tool any more).

## Properties

| Property | Value |
|---|---|
| Name | Same as the notebook title. One source: its title without channel or site suffixes. Several sources or research: the topic in title case, at most 60 characters. A card with that Name already exists (the same source in another format): append the format, "<title> (Debate)", and use it for a new notebook too. |
| Theme | Exactly one existing option: the one for the main subject (what most of the summary is about); when several fit, still that one, and note the choice in the run notes. Nothing fits: add an option with `notion-update-data-source` (`ALTER COLUMN "Theme" SET SELECT(...)` listing every existing option plus the new one), then tell the user in the report. |
| Tags | 3 to 6 specific, lowercase. Reuse first: fetch the data source, and where an existing tag fits, use it instead of a near-synonym (`active listening`, not also `listening skills`). Only then create new ones; add the option first if card creation rejects it. |
| For | `for_default` from the config ("Me" by default) unless the user said "for <name>"; add a new option for a new name. |
| Scenario | Single, Multiple or Research |
| Source types | Podcast, Interview, Talk, Video, Article, Paper, Book, File, as a JSON array: the content type plus the medium of every source that went in (a YouTube interview is Interview and Video; a podcast episode is Podcast, plus Interview when it is one). |
| Format | Deep Dive, Brief, Critique, Debate |
| Length | Short, Default, Long; empty for Brief |
| First-time topic | `__YES__` or `__NO__` |
| Notebook | The notebook URL; empty in fallback. The property is named "Notebook", so no `userDefined:` prefix. |

Sources table: the Source column shows the paper's or page's real title (the renamed one), not NotebookLM's raw title. Every unticked source is a row with In or out = Out and the reason. Origin: You (the user's links), Claude (your picks, swaps and alternatives), NotebookLM (Deep Research), Both (Claude and NotebookLM found it). A swap is two rows: the user's original Out with the reason, the replacement In with "same episode as the user's <Spotify> link" or similar. Candidates you looked at for a swap and didn't use get no row.

Themes and tags: always read the options from the live schema (`notion-fetch` the data source) before choosing; never from a list in this file.

## Card body

Sections in this order, in Notion enhanced Markdown. In plain text outside code blocks, escape these characters with a backslash: backslash, asterisk, tilde, backtick, dollar, square brackets, angle brackets, curly brackets, pipe, caret. Write file names as inline code (`rules.md`, `length.py`): as plain text Notion turns them into web links (".md" is a country domain).

````
## Summary
<NotebookLM summary verbatim; with two or more sources, the chat summary without its citation numbers>
## Sources
<table header-row="true">
	<tr>
		<td>Source</td>
		<td>Type</td>
		<td>Origin</td>
		<td>In or out</td>
		<td>Reason</td>
	</tr>
	<tr>
		<td>[<title>](<url>)</td>
		<td><type></td>
		<td>You, Claude, NotebookLM or Both</td>
		<td>In or Out</td>
		<td><one line></td>
	</tr>
</table>
## Prompt used
```text
<the instruction block, verbatim>
```
## Run notes
- <cuts, Spotify swaps, Generate later, fallback, resumed; "none" when nothing happened>
````
