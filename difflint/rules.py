"""Individual checks run against each added line of a diff."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

from .parser import AddedLine


@dataclass
class Finding:
    path: str
    lineno: int
    rule_id: str
    message: str


@dataclass
class Rule:
    rule_id: str
    message: str
    check: Callable[[str], bool]


def _has_trailing_whitespace(text: str) -> bool:
    stripped = text.rstrip("\n\r")
    return stripped != "" and stripped != stripped.rstrip(" \t")


def _is_conflict_marker(text: str) -> bool:
    stripped = text.rstrip("\n\r")
    return (
        stripped.startswith("<<<<<<<")
        or stripped.startswith("=======")
        or stripped.startswith(">>>>>>>")
    )


def make_line_length_rule(max_length: int) -> Rule:
    def check(text: str) -> bool:
        return len(text.rstrip("\n\r")) > max_length

    return Rule(
        rule_id="line-too-long",
        message=f"line exceeds {max_length} characters",
        check=check,
    )


DEFAULT_RULES = [
    Rule("trailing-whitespace", "trailing whitespace", _has_trailing_whitespace),
    Rule("conflict-marker", "unresolved merge conflict marker", _is_conflict_marker),
]


def run_rules(added_lines: Iterable[AddedLine], rules: Iterable[Rule]) -> List[Finding]:
    findings = []
    for line in added_lines:
        for rule in rules:
            if rule.check(line.text):
                findings.append(Finding(line.path, line.lineno, rule.rule_id, rule.message))
    return findings
