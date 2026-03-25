"""Tests for nesting, unhug, and indentation behavior."""

import unittest

from trailing_comma import fix_trailing_commas


class TestNested(unittest.TestCase):

    def test_nested_calls(self):
        source = """\
            result = outer(
                inner(a, b, c),
                inner(d, e, f)
            )
        """
        expected = """\
            result = outer(
                inner(a, b, c),
                inner(d, e, f),
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_nested_both_multiline(self):
        source = """\
            result = outer(
                inner(
                    a, b
                )
            )
        """
        expected = """\
            result = outer(
                inner(
                    a, b,
                ),
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_list_inside_call(self):
        source = """\
            foo(
                [
                    1, 2, 3
                ]
            )
        """
        expected = """\
            foo(
                [
                    1, 2, 3,
                ],
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)


class TestUnhug(unittest.TestCase):

    def test_unhug_close(self):
        source = """\
            foo(
                a,
                b, c)
        """
        expected = """\
            foo(
                a,
                b, c,
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_unhug_open(self):
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
        self.assertEqual(fix_trailing_commas(source), expected)


class TestIndentation(unittest.TestCase):

    def test_closing_brace_dedented(self):
        source = """\
            def load(root: str, date_from: dt.date,
                     ) -> dict[dt.date, float]:
                pass
        """
        expected = """\
            def load(
                root: str, date_from: dt.date,
            ) -> dict[dt.date, float]:
                pass
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_indented_call(self):
        source = """\
            if True:
                foo(
                    a, b
                )
        """
        expected = """\
            if True:
                foo(
                    a, b,
                )
        """
        self.assertEqual(fix_trailing_commas(source), expected)


class TestIdempotent(unittest.TestCase):

    def test_idempotent_call(self):
        source = """\
            foo(
                a, b
            )
        """
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)

    def test_idempotent_removal(self):
        source = 'foo(a, b,)\n'
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)


if __name__ == '__main__':
    unittest.main()
