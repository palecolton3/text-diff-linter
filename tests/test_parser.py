import unittest

from difflint.parser import AddedLine, iter_added_lines


class IterAddedLinesTests(unittest.TestCase):
    def test_single_hunk_tracks_new_line_numbers(self):
        diff = (
            "--- a/foo.py\n"
            "+++ b/foo.py\n"
            "@@ -1,3 +1,4 @@\n"
            " unchanged\n"
            "-removed\n"
            "+added one\n"
            "+added two\n"
            " trailing context\n"
        )
        lines = list(iter_added_lines(diff))
        self.assertEqual(
            lines,
            [
                AddedLine(path="foo.py", lineno=2, text="added one"),
                AddedLine(path="foo.py", lineno=3, text="added two"),
            ],
        )

    def test_hunk_header_without_new_count(self):
        # "@@ -1 +1 @@" form (no ",count") is valid for single-line hunks.
        diff = "+++ b/foo.py\n@@ -1 +1 @@\n+only line\n"
        lines = list(iter_added_lines(diff))
        self.assertEqual(lines, [AddedLine(path="foo.py", lineno=1, text="only line")])

    def test_multiple_hunks_resume_line_count(self):
        diff = (
            "+++ b/foo.py\n"
            "@@ -1,2 +1,2 @@\n"
            " one\n"
            "+two\n"
            "@@ -10,2 +11,3 @@\n"
            " ten\n"
            "+eleven\n"
            "+twelve\n"
        )
        lines = list(iter_added_lines(diff))
        self.assertEqual(
            [(l.lineno, l.text) for l in lines],
            [(2, "two"), (12, "eleven"), (13, "twelve")],
        )

    def test_multiple_files_reset_line_count(self):
        diff = (
            "+++ b/a.py\n"
            "@@ -1,1 +1,2 @@\n"
            " a\n"
            "+a added\n"
            "+++ b/b.py\n"
            "@@ -5,1 +5,2 @@\n"
            " b\n"
            "+b added\n"
        )
        lines = list(iter_added_lines(diff))
        self.assertEqual(
            [(l.path, l.lineno, l.text) for l in lines],
            [("a.py", 2, "a added"), ("b.py", 6, "b added")],
        )

    def test_no_newline_at_end_of_file_marker_is_ignored(self):
        diff = "+++ b/foo.py\n@@ -1,1 +1,1 @@\n+added\n\\ No newline at end of file\n"
        lines = list(iter_added_lines(diff))
        self.assertEqual(lines, [AddedLine(path="foo.py", lineno=1, text="added")])

    def test_lines_outside_a_hunk_are_skipped(self):
        diff = "diff --git a/foo.py b/foo.py\nindex 111..222 100644\n+++ b/foo.py\n"
        self.assertEqual(list(iter_added_lines(diff)), [])

    def test_missing_path_header_falls_back_to_stdin_marker(self):
        diff = "@@ -1,1 +1,1 @@\n+added\n"
        lines = list(iter_added_lines(diff))
        self.assertEqual(lines[0].path, "<stdin>")

    def test_dev_null_path_is_kept_as_is(self):
        diff = "+++ /dev/null\n@@ -1,1 +0,0 @@\n-removed only\n"
        self.assertEqual(list(iter_added_lines(diff)), [])

    def test_plus_plus_plus_header_strips_prefix_and_timestamp(self):
        diff = "+++ b/foo.py\t2024-01-01 00:00:00\n@@ -1,1 +1,1 @@\n+added\n"
        lines = list(iter_added_lines(diff))
        self.assertEqual(lines[0].path, "foo.py")


if __name__ == "__main__":
    unittest.main()
