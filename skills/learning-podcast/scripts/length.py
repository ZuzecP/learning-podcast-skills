"""Audio Overview length for a set of sources (spec section 7).

One source: Long at or above its kind's threshold, else Default.
More than one source: always Long. Long exists only for Deep Dive
(measured 2026-10-06: Critique and Debate offer Short and Default;
Brief has no length), so other formats get Default. Brief: None.
"""
from __future__ import annotations

import argparse
import sys

THRESHOLDS = {
    "conversation": ("minutes", 60),
    "talk": ("minutes", 30),
    "written": ("words", 3000),
}
OTHER_BY_UNIT = {"minutes": 60, "words": 3000}
FORMATS = ["Deep Dive", "Brief", "Critique", "Debate"]
LONG_FORMATS = {"Deep Dive"}


def _wants_long(sources: list[dict]) -> bool:
    if not sources:
        raise ValueError("no sources")
    if len(sources) > 1:
        return True
    src = sources[0]
    kind = src.get("kind")
    if kind in THRESHOLDS:
        unit, limit = THRESHOLDS[kind]
        if unit not in src:
            raise ValueError(f"a {kind} source needs '{unit}'")
    elif kind == "other":
        unit = "minutes" if "minutes" in src else "words"
        if unit not in src:
            raise ValueError("an other source needs 'minutes' or 'words'")
        limit = OTHER_BY_UNIT[unit]
    else:
        raise ValueError(f"unknown kind: {kind}")
    return src[unit] >= limit


def choose_length(sources: list[dict], fmt: str = "Deep Dive") -> str | None:
    if fmt not in FORMATS:
        raise ValueError(f"unknown format: {fmt}")
    if fmt == "Brief":
        return None
    long = _wants_long(sources)
    return "Long" if long and fmt in LONG_FORMATS else "Default"


def parse_source(spec: str) -> dict:
    kind, _, value = spec.partition(":")
    if not kind or not value or value[-1] not in "mw" or not value[:-1].isdigit():
        raise ValueError(f"bad source spec {spec!r}: use KIND:<n>m or KIND:<n>w")
    unit = "minutes" if value[-1] == "m" else "words"
    return {"kind": kind, unit: int(value[:-1])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", default="Deep Dive", choices=FORMATS)
    parser.add_argument("sources", nargs="*", help="e.g. conversation:45m talk:35m written:3200w other:20m")
    args = parser.parse_args(argv)
    try:
        result = choose_length([parse_source(s) for s in args.sources], args.format)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(result or "none (Brief)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
