"""Command line entry point: read diffs from files or stdin, report findings."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .parser import iter_added_lines
from .rules import DEFAULT_RULES, make_line_length_rule, run_rules


def _read_inputs(paths: List[str]) -> str:
    if not paths or paths == ["-"]:
        return sys.stdin.read()

    chunks = []
    for path in paths:
        if path == "-":
            chunks.append(sys.stdin.read())
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                chunks.append(handle.read())
    return "\n".join(chunks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="difflint",
        description="Check the added lines of a unified diff for common problems.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="diff files to check; omit or pass - to read from stdin",
    )
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=100,
        help="longest allowed line before line-too-long fires (default: 100)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    diff_text = _read_inputs(args.paths)

    rules = list(DEFAULT_RULES) + [make_line_length_rule(args.max_line_length)]
    findings = run_rules(iter_added_lines(diff_text), rules)

    for finding in sorted(findings, key=lambda f: (f.path, f.lineno)):
        print(f"{finding.path}:{finding.lineno}: [{finding.rule_id}] {finding.message}")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
