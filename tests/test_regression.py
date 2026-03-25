"""Regression tests for specific bugs found during development."""

import unittest

from trailing_comma import fix_trailing_commas


class TestWindowsNewlines(unittest.TestCase):
    """The original add-trailing-comma bug: stdin on Windows produces
    \\r\\r\\n because binary read + text-mode print double the carriage return."""

    def test_crlf_preserved(self):
        source = "foo(\r\n    a, b\r\n)\r\n"
        expected = "foo(\r\n    a, b,\r\n)\r\n"
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_no_double_cr(self):
        source = "foo(\r\n    a, b\r\n)\r\n"
        result = fix_trailing_commas(source)
        self.assertNotIn('\r\r', result)


class TestYapfCycle(unittest.TestCase):
    """yapf and add-trailing-comma fight on annotated defs: yapf produces
    continuation-indent, add-trailing-comma dedents, yapf re-indents, forever.
    We break the cycle by unhugging + dedenting in one pass."""

    def test_continuation_indent_fixed(self):
        source = """\
            def load_daily_sigma(root: str, date_from: dt.date,
                                 ) -> dict[dt.date, float]:
                pass
        """
        expected = """\
            def load_daily_sigma(
                root: str, date_from: dt.date,
            ) -> dict[dt.date, float]:
                pass
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_idempotent_after_fix(self):
        source = """\
            def load_daily_sigma(root: str, date_from: dt.date,
                                 ) -> dict[dt.date, float]:
                pass
        """
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)


class TestFirstLineIndent(unittest.TestCase):
    """Bug: initial_indent defaulted to 0 when the opening brace was on the
    first line of the source (no preceding newline). The closing brace was
    then "fixed" to column 0, destroying the indentation.

    Root cause: the indent detection walks backward from the brace looking for
    a NEWLINE token. On the first line there is none, so it fell through to
    initial_indent = 0 regardless of actual indentation."""

    def test_indented_source_preserves_closing_brace(self):
        # The opening ( is on the first line — no newline precedes it.
        # Without the fix, the ) gets moved to column 0.
        source = """\
            foo(
                a, b
            )
        """
        expected = """\
            foo(
                a, b,
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_no_change_construct_keeps_indent(self):
        # Even constructs we don't add commas to (generators) must not
        # have their closing brace moved.
        source = """\
            sum(
                x for x in range(10)
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)


class TestUnhugClosingBraceSkew(unittest.TestCase):
    """Bug: when unhugging an open brace (content on same line as opening
    brace), the re-indentation scan included the closing brace's whitespace
    in its min_indent calculation. Since the closing brace is typically at a
    lower indent than the content, this inflated the content's indentation.

    Example: foo(a,\\n        b, c\\n    )
    The closing ) is at 4 spaces, content b is at 8. min_indent picked up
    4 from ), then recomputed b as 8 - 4 + 8 = 12 instead of keeping it at 8.

    Root cause: the scan range included the indent token immediately before
    the closing brace. That token is handled separately by the closing-brace
    fix and should be excluded from content re-indentation."""

    def test_unhug_open_content_not_inflated(self):
        source = """\
            foo(a,
                b, c
            )
        """
        expected = """\
            foo(
                a,
                b, c,
            )
        """
        result = fix_trailing_commas(source)
        self.assertEqual(result, expected)

    def test_unhug_open_multiple_content_lines(self):
        source = """\
            foo(a,
                b,
                c
            )
        """
        expected = """\
            foo(
                a,
                b,
                c,
            )
        """
        result = fix_trailing_commas(source)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
