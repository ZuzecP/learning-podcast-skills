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
import argparse
import json
import re
import sys
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


_KEY_LINE = re.compile(r"^([a-z_]+):(?: (.*))?$")
_ESCAPE = re.compile(r'\\(["\\n])')


def _parse_scalar(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return _ESCAPE.sub(lambda m: "\n" if m.group(1) == "n" else m.group(1), raw[1:-1])
    if raw == "true":
        return True
    if raw == "false":
        return False
    return raw


def _as_list(value):
    """A list from a list, an inline [a, b] list or a single bare value."""
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        return [_parse_scalar(part) for part in text[1:-1].split(",") if part.strip()]
    return [text] if text else []


def read_card(path):
    """Parse a card file written by this module; None when it is not one."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return None
    end = lines.index("---", 1)
    card = {"name": Path(path).stem}
    key = None
    for line in lines[1:end]:
        item = re.match(r"^\s*- (.*)$", line)
        if item and key is not None and isinstance(card.get(key), list):
            card[key].append(_parse_scalar(item.group(1)))
            continue
        match = _KEY_LINE.match(line)
        if not match:
            continue
        key, raw = match.group(1), match.group(2)
        if raw is None:
            card[key] = [] if key in ("tags", "source_types") else ""
        elif raw == "[]":
            card[key] = []
        else:
            card[key] = _parse_scalar(raw)
    if "theme" not in card:
        return None
    for list_key in ("tags", "source_types"):
        card[list_key] = _as_list(card.get(list_key, []))
    body = lines[end + 1:]
    summary = []
    inside = False
    for line in body:
        if line == "## Summary":
            inside = True
        elif inside and line.startswith("## "):
            break
        elif inside:
            summary.append(line)
    card["summary"] = "\n".join(summary).strip()
    return card


def _cards_in(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise CardError("no_folder", str(folder))
    found = []
    for path in sorted(folder.glob("*.md")):
        try:
            card = read_card(path)
        except (OSError, UnicodeDecodeError):
            continue
        if card is not None:
            found.append(card)
    return found


def scan(folder):
    """Distinct themes, tags, for values and card names found in the folder."""
    found = _cards_in(folder)
    tags = {tag for card in found for tag in card.get("tags", [])}
    return {
        "themes": sorted({c["theme"] for c in found if c.get("theme")}),
        "tags": sorted(tags),
        "for": sorted({c["for"] for c in found if c.get("for")}),
        "names": sorted(c["name"] for c in found),
    }


def find(folder, query):
    """Cards where any keyword occurs in name, theme, tags or summary."""
    words = query.lower().split()
    if not words:
        raise CardError("bad_input", "the query has no keywords")
    hits = []
    for card in _cards_in(folder):
        text = " ".join([card["name"], card.get("theme", ""), *card.get("tags", []), card["summary"]]).lower()
        if any(word in text for word in words):
            hits.append({"name": card["name"], "theme": card.get("theme", ""), "tags": card.get("tags", [])})
    return sorted(hits, key=lambda c: c["name"])


def name_info(folder, name):
    """The file stem for a name and whether a card with that stem exists."""
    stem = sanitize_name(name)
    folder = Path(folder)
    if not folder.is_dir():
        raise CardError("no_folder", str(folder))
    return {"stem": stem, "exists": (folder / f"{stem}.md").exists()}


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CardError("bad_input", message)


def _folder(value):
    if not Path(value).is_absolute():
        raise CardError("bad_input", "--folder must be an absolute path")
    return Path(value)


def _build_parser():
    parser = _Parser(prog="cards.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    for command in ("name", "write", "scan", "find"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--folder", required=True)
        if command == "name":
            cmd.add_argument("--name", required=True)
        elif command == "write":
            cmd.add_argument("--card", required=True)
        elif command == "find":
            cmd.add_argument("--query", required=True)
    return parser


def _run(args):
    folder = _folder(args.folder)
    if args.command == "name":
        return name_info(folder, args.name)
    if args.command == "scan":
        return scan(folder)
    if args.command == "find":
        return {"cards": find(folder, args.query)}
    try:
        card = json.loads(Path(args.card).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise CardError("bad_input", f"cannot read the card file: {error}")
    if not isinstance(card, dict):
        raise CardError("bad_input", "the card file must hold a JSON object")
    return {"path": str(write_card(folder, card))}


def main(argv):
    try:
        result = {"ok": True, **_run(_build_parser().parse_args(argv))}
        code = 0
    except CardError as error:
        result = {"ok": False, "reason": error.reason, "detail": error.detail}
        code = 2
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
