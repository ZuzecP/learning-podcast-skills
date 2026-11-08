"""Build the Audio Overview instruction block from references/rules.md (spec section 6).

All texts are copied from rules.md verbatim; nothing is filled in. Sections are
included per format, names flag and first-time flag, then removed in the
rules.md cut order while the block is longer than the box limit.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RULES = Path(__file__).resolve().parents[1] / "references" / "rules.md"
FORMATS = ["Deep Dive", "Brief", "Critique", "Debate"]
ORDER = ["NAMES", "TONE", "FACTS", "BRIEF", "DEPTH", "LEVELS", "ACTIONS", "GAPS", "STUDY FURTHER"]
CUT_ORDER = ["STUDY FURTHER", "ACTIONS", "LEVELS", "DEPTH", "GAPS"]
NOT_IN_BRIEF = {"DEPTH", "LEVELS", "ACTIONS", "STUDY FURTHER"}
REQUIRED_TEXTS = [
    "NAMES", "TONE", "FACTS", "BRIEF", "DEPTH", "LEVELS", "ACTIONS", "GAPS", "GAPS (brief)", "STUDY FURTHER",
]
TEXT_LINE = re.compile(r"^([A-Z][A-Z ]*?)(?: \(([a-z]+)\))?: (.+)$")


def load_rules(path: Path = RULES) -> tuple[dict[str, str], int | None]:
    text = path.read_text(encoding="utf-8")
    found = re.search(r"^Instruction box limit: (\d+) characters", text, re.MULTILINE)
    limit = int(found.group(1)) if found else None
    if "## Section texts" not in text:
        raise ValueError(f"{path} has no '## Section texts' heading")
    texts = {}
    for line in text.split("## Section texts", 1)[1].splitlines():
        match = TEXT_LINE.match(line)
        if match:
            label, variant, content = match.groups()
            texts[f"{label} ({variant})" if variant else label] = content
    missing = [key for key in REQUIRED_TEXTS if key not in texts]
    if missing:
        raise ValueError(f"{path} is missing texts: {', '.join(missing)}")
    return texts, limit


def included(fmt: str, first_time: bool, names: bool) -> list[str]:
    labels = []
    for label in ORDER:
        if label == "NAMES" and not names:
            continue
        if label == "BRIEF" and fmt != "Brief":
            continue
        if label in NOT_IN_BRIEF and fmt == "Brief":
            continue
        if label == "STUDY FURTHER" and not first_time:
            continue
        labels.append(label)
    return labels


def render(labels: list[str], texts: dict[str, str], fmt: str) -> str:
    lines = []
    for label in labels:
        body = texts["GAPS (brief)"] if label == "GAPS" and fmt == "Brief" else texts[label]
        lines.append(f"{label}: {body}")
    return "\n".join(lines) + "\n"


def assemble(
    fmt: str,
    names: bool = False,
    first_time: bool = False,
    limit: int | None = None,
    rules_path: Path = RULES,
) -> tuple[str, list[str]]:
    if fmt not in FORMATS:
        raise ValueError(f"unknown format: {fmt}")
    texts, rules_limit = load_rules(rules_path)
    limit = rules_limit if limit is None else limit
    labels = included(fmt, first_time, names)
    block = render(labels, texts, fmt)
    cuts: list[str] = []
    for label in CUT_ORDER:
        if limit is None or len(block) <= limit:
            break
        if label in labels:
            labels.remove(label)
            cuts.append(label)
            block = render(labels, texts, fmt)
    if limit is not None and len(block) > limit:
        raise ValueError(f"too long even after all cuts: {len(block)} characters, limit {limit}")
    return block, cuts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", required=True, choices=FORMATS)
    parser.add_argument("--names", action="store_true", help="a person named in the sources has special characters in their name")
    parser.add_argument("--first-time", action="store_true")
    parser.add_argument("--limit", type=int, help="override the limit in rules.md")
    parser.add_argument("--rules", type=Path, default=RULES, help="rules file to use instead of the shipped rules.md")
    args = parser.parse_args(argv)
    try:
        block, cuts = assemble(args.format, args.names, args.first_time, args.limit, args.rules)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    sys.stdout.write(block)
    print(f"notes: {len(block)} characters | cuts: {', '.join(cuts) or 'none'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
