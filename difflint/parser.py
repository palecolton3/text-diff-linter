"""Parsing of unified diff text into per-line records.

We only ever look at the "new" side of each hunk, since that is the
content a reviewer can still change. Context and removed lines are
skipped but still walked so the new-file line counter stays accurate.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AddedLine:
    path: str
    lineno: int
    text: str


def iter_added_lines(diff_text: str):
    path = None
    new_lineno = None

    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            path = _strip_diff_path(raw[4:])
            new_lineno = None
            continue

        if raw.startswith("@@ "):
            new_lineno = _parse_hunk_start(raw)
            continue

        if new_lineno is None:
            # Outside of any hunk (file headers, "diff --git" lines, etc.)
            continue

        if raw.startswith("+") and not raw.startswith("+++"):
            yield AddedLine(path=path or "<stdin>", lineno=new_lineno, text=raw[1:])
            new_lineno += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            continue
        elif raw.startswith("\\"):
            # "\ No newline at end of file" - not a real line
            continue
        else:
            new_lineno += 1


def _strip_diff_path(field: str) -> str:
    field = field.split("\t", 1)[0].strip()
    if field == "/dev/null":
        return field
    for prefix in ("b/", "a/"):
        if field.startswith(prefix):
            return field[len(prefix):]
    return field


def _parse_hunk_start(header: str) -> int:
    # header looks like: @@ -12,7 +15,8 @@ optional section heading
    try:
        new_part = header.split("+", 1)[1].split(" ", 1)[0]
        start = new_part.split(",", 1)[0]
        return int(start)
    except (IndexError, ValueError):
        return 1
