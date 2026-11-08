#!/bin/sh
# Fail when a file in the tree contains something personal.
# Usage: check-public.sh [ROOT]   (default: the repository root)
# Exit 0 when clean; exit 1 and one "path:line: label" line per hit.
# Skips .git/, .superpowers/ and the two files that hold the patterns themselves.

ROOT=${1:-$(cd "$(dirname "$0")/.." && pwd)}
cd "$ROOT" || exit 2

found=0
check() {
    label=$1
    pattern=$2
    hits=$(grep -rnIiE \
        --exclude-dir=.git --exclude-dir=.superpowers \
        --exclude=check-public.sh --exclude=test_check_public.py \
        -e "$pattern" . 2>/dev/null |
        sed -E "s|^\./||; s|^([^:]*):([0-9]+):.*|\1:\2: $label|")
    if [ -n "$hits" ]; then
        printf '%s\n' "$hits"
        found=1
    fi
}

check "home path" '/Users/'
check "32-char id" '(^|[^0-9a-f])[0-9a-f]{32}([^0-9a-f]|$)'
check "collection url" 'collection://'
check "notion page url" 'app\.notion\.com/p/'
check "notion.so url" 'notion\.so/'
check "gmail address" '@gmail\.com'
check "old fixture name" 'sedova'
check "old guest name" 'Šedivá'

exit "$found"
