#!/bin/sh
# Link every skill in this repo into a project folder's .claude/skills/.
# Usage: install.sh [--force] PROJECT_DIR
# Idempotent. Refuses (exit 1, nothing changed) when a target is a real file or
# directory, or a link that points elsewhere; --force repoints such a link.

force=0
if [ "$1" = "--force" ]; then
    force=1
    shift
fi
project=$1
if [ -z "$project" ] || [ ! -d "$project" ]; then
    echo "error: project folder not found: $project" >&2
    exit 1
fi

root=$(cd "$(dirname "$0")/.." && pwd)
dest="$project/.claude/skills"

# First pass: check every target, change nothing.
for dir in "$root"/skills/*/; do
    name=$(basename "$dir")
    target="$dest/$name"
    if [ -L "$target" ]; then
        if [ "$(readlink "$target")" != "$root/skills/$name" ] && [ "$force" -eq 0 ]; then
            echo "error: $target points elsewhere; use --force to repoint it" >&2
            exit 1
        fi
    elif [ -e "$target" ]; then
        echo "error: $target exists and is not a link; remove or move it first" >&2
        exit 1
    fi
done

mkdir -p "$dest" || exit 1
for dir in "$root"/skills/*/; do
    name=$(basename "$dir")
    ln -sfn "$root/skills/$name" "$dest/$name" || exit 1
    echo "linked $name"
done
