#!/usr/bin/env python3
"""Write and read podcast cards as Markdown files (one file per card).

Python 3 standard library only. A card file is YAML frontmatter followed by
four body sections: Summary, Sources, Prompt used, Run notes.

Card dict (input of write_card / render_card):
  name, theme, tags (list), for, scenario, source_types (list), format,
  length (optional), first_time_topic (bool), notebook (may be ""),
  created (ISO string), summary, sources (list of dicts with title, url,
  type, origin, in_out, reason), prompt, run_notes (list of str).

Refusals are CardError with a reason code: exists, outside_folder,
no_folder, bad_input, io_error.
"""
import re
from pathlib import Path

FORBIDDEN = re.compile(r'[/\\:*?"<>|\x00-\x1f]')
FRONTMATTER_KEYS = [
    "theme", "tags", "for", "scenario", "source_types", "format",
    "length", "first_time_topic", "notebook", "created",
]
REQUIRED = [
    "name", "theme", "tags", "for", "scenario", "source_types", "format",
    "first_time_topic", "notebook", "created", "summary", "sources",
    "prompt", "run_notes",
]
LIST_KEYS = ("tags", "source_types", "sources", "run_notes")
RESERVED_WORDS = {"true", "false", "null", "yes", "no", "on", "off", "~"}
NUMBER = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
RISKY_CHARS = set(':#&"\'\n')
RISKY_START = set("-?[]{}!|>%@*,`")


class CardError(Exception):
    def __init__(self, reason, detail=""):
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


def sanitize_name(name):
    """File-name stem for a card name; CardError(bad_input) when nothing is left."""
    stem = FORBIDDEN.sub(" ", str(name))
    stem = re.sub(r"\s+", " ", stem).strip(" .")
    if not stem:
        raise CardError("bad_input", "the name has no usable characters")
    return stem


def yaml_scalar(value):
    """A YAML scalar: bare when safe, double-quoted otherwise."""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    risky = (
        text == ""
        or text != text.strip()
        or any(c in RISKY_CHARS for c in text)
        or text[0] in RISKY_START
        or text.lower() in RESERVED_WORDS
        or NUMBER.match(text) is not None
    )
    if not risky:
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _cell(value):
    return str(value).replace("\n", " ").replace("|", "\\|")


def _frontmatter(card):
    lines = ["---"]
    for key in FRONTMATTER_KEYS:
        value = card.get(key)
        if key == "length" and not value:
            continue
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                lines.extend(f"  - {yaml_scalar(item)}" for item in value)
        elif value is None or value == "":
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def _sources_table(sources):
    rows = ["| Source | Type | Origin | In or out | Reason |", "|---|---|---|---|---|"]
    for src in sources:
        title = _cell(src.get("title", ""))
        url = _cell(src.get("url", ""))
        first = f"[{title}]({url})" if url else title
        cells = [first] + [_cell(src.get(k, "")) for k in ("type", "origin", "in_out", "reason")]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _check(card):
    missing = [key for key in REQUIRED if key not in card]
    if missing:
        raise CardError("bad_input", "missing keys: " + ", ".join(missing))
    for key in LIST_KEYS:
        if not isinstance(card[key], list):
            raise CardError("bad_input", f"{key} must be a list")
    for src in card["sources"]:
        if not isinstance(src, dict):
            raise CardError("bad_input", "each source must be an object")


def render_card(card):
    """The full text of a card file."""
    _check(card)
    notes = card["run_notes"] or ["none"]
    parts = [
        _frontmatter(card),
        "",
        "## Summary",
        str(card["summary"]),
        "## Sources",
        _sources_table(card["sources"]),
        "## Prompt used",
        "```text",
        str(card["prompt"]),
        "```",
        "## Run notes",
    ]
    parts.extend(f"- {note}" for note in notes)
    return "\n".join(parts) + "\n"


def write_card(folder, card):
    """Write the card as <folder>/<stem>.md; never overwrites. Returns the path."""
    folder = Path(folder)
    _check(card)
    stem = sanitize_name(card["name"])
    if not folder.is_dir():
        raise CardError("no_folder", str(folder))
    path = folder / f"{stem}.md"
    if path.resolve().parent != folder.resolve():
        raise CardError("outside_folder", str(path))
    text = render_card(card)
    try:
        with open(path, "x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError:
        raise CardError("exists", str(path))
    except OSError as error:
        raise CardError("io_error", str(error))
    return path
