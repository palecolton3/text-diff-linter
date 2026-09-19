import unittest

from difflint.parser import AddedLine
from difflint.rules import (
    DEFAULT_RULES,
    Finding,
    _has_trailing_whitespace,
    _is_conflict_marker,
    make_line_length_rule,
    run_rules,
)


class TrailingWhitespaceTests(unittest.TestCase):
    def test_flags_trailing_space(self):
        self.assertTrue(_has_trailing_whitespace("foo = 1 "))

    def test_flags_trailing_tab(self):
        self.assertTrue(_has_trailing_whitespace("foo = 1\t"))

    def test_ignores_clean_line(self):
        self.assertFalse(_has_trailing_whitespace("foo = 1"))

    def test_ignores_empty_line(self):
        self.assertFalse(_has_trailing_whitespace(""))

    def test_flags_line_that_is_only_whitespace(self):
        self.assertTrue(_has_trailing_whitespace("   "))


class ConflictMarkerTests(unittest.TestCase):
    def test_flags_start_marker(self):
        self.assertTrue(_is_conflict_marker("<<<<<<< HEAD"))

    def test_flags_separator_marker(self):
        self.assertTrue(_is_conflict_marker("======="))

    def test_flags_end_marker(self):
        self.assertTrue(_is_conflict_marker(">>>>>>> branch-name"))

    def test_ignores_normal_line(self):
        self.assertFalse(_is_conflict_marker("some code"))

    def test_ignores_marker_that_is_not_at_line_start(self):
        self.assertFalse(_is_conflict_marker("    <<<<<<< HEAD"))


class LineLengthRuleTests(unittest.TestCase):
    def test_line_at_limit_is_not_flagged(self):
        rule = make_line_length_rule(10)
        self.assertFalse(rule.check("x" * 10))

    def test_line_over_limit_is_flagged(self):
        rule = make_line_length_rule(10)
        self.assertTrue(rule.check("x" * 11))

    def test_trailing_newline_is_not_counted(self):
        rule = make_line_length_rule(5)
        self.assertFalse(rule.check("x" * 5 + "\n"))


class RunRulesTests(unittest.TestCase):
    def test_collects_one_finding_per_matching_rule(self):
        lines = [
            AddedLine(path="foo.py", lineno=1, text="clean line"),
            AddedLine(path="foo.py", lineno=2, text="dirty line "),
            AddedLine(path="foo.py", lineno=3, text="<<<<<<< HEAD"),
        ]
        findings = run_rules(lines, DEFAULT_RULES)
        self.assertEqual(
            findings,
            [
                Finding("foo.py", 2, "trailing-whitespace", "trailing whitespace"),
                Finding(
                    "foo.py",
                    3,
                    "conflict-marker",
                    "unresolved merge conflict marker",
                ),
            ],
        )

    def test_no_findings_for_clean_input(self):
        lines = [AddedLine(path="foo.py", lineno=1, text="clean line")]
        self.assertEqual(run_rules(lines, DEFAULT_RULES), [])


if __name__ == "__main__":
    unittest.main()
