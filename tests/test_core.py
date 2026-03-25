"""Tests for trailing_comma.fix_trailing_commas."""

import textwrap
import unittest

from trailing_comma import fix_trailing_commas


class TestAddComma(unittest.TestCase):
    """Multi-line constructs that should get a trailing comma added."""

    def test_function_call(self):
        source = textwrap.dedent("""\
            foo(
                a, b
            )
        """)
        expected = textwrap.dedent("""\
            foo(
                a, b,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_function_call_already_has_comma(self):
        source = textwrap.dedent("""\
            foo(
                a, b,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_function_def(self):
        source = textwrap.dedent("""\
            def foo(
                a, b
            ):
                pass
        """)
        expected = textwrap.dedent("""\
            def foo(
                a, b,
            ):
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_async_def(self):
        source = textwrap.dedent("""\
            async def foo(
                a, b
            ):
                pass
        """)
        expected = textwrap.dedent("""\
            async def foo(
                a, b,
            ):
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_import(self):
        source = textwrap.dedent("""\
            from os.path import (
                join,
                exists
            )
        """)
        expected = textwrap.dedent("""\
            from os.path import (
                join,
                exists,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_list(self):
        source = textwrap.dedent("""\
            x = [
                1, 2, 3
            ]
        """)
        expected = textwrap.dedent("""\
            x = [
                1, 2, 3,
            ]
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_dict(self):
        source = textwrap.dedent("""\
            x = {
                "a": 1,
                "b": 2
            }
        """)
        expected = textwrap.dedent("""\
            x = {
                "a": 1,
                "b": 2,
            }
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_set(self):
        source = textwrap.dedent("""\
            x = {
                1, 2, 3
            }
        """)
        expected = textwrap.dedent("""\
            x = {
                1, 2, 3,
            }
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_tuple(self):
        source = textwrap.dedent("""\
            x = (
                1, 2, 3
            )
        """)
        expected = textwrap.dedent("""\
            x = (
                1, 2, 3,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)


class TestRemoveComma(unittest.TestCase):
    """Single-line constructs that should get a trailing comma removed."""

    def test_call(self):
        self.assertEqual(
            fix_trailing_commas('foo(a, b,)\n'),
            'foo(a, b)\n',
        )

    def test_call_trailing_space(self):
        self.assertEqual(
            fix_trailing_commas('foo(a, b, )\n'),
            'foo(a, b)\n',
        )

    def test_list(self):
        self.assertEqual(
            fix_trailing_commas('x = [1, 2, 3,]\n'),
            'x = [1, 2, 3]\n',
        )

    def test_multi_element_tuple(self):
        self.assertEqual(
            fix_trailing_commas('x = (1, 2, 3,)\n'),
            'x = (1, 2, 3)\n',
        )

    def test_single_element_tuple_preserved(self):
        source = 'x = (1,)\n'
        self.assertEqual(fix_trailing_commas(source), source)


class TestNoChange(unittest.TestCase):
    """Constructs that should not be modified."""

    def test_generator(self):
        source = textwrap.dedent("""\
            sum(
                x for x in range(10)
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_list_comprehension(self):
        source = textwrap.dedent("""\
            x = [
                item
                for item in things
            ]
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_dict_comprehension(self):
        source = textwrap.dedent("""\
            x = {
                k: v
                for k, v in items
            }
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_parenthesized_expression(self):
        source = textwrap.dedent("""\
            x = (
                long_expr + other
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_class_bases(self):
        source = textwrap.dedent("""\
            class Foo(
                Bar, Baz
            ):
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_empty_call(self):
        source = textwrap.dedent("""\
            foo(
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_single_line_no_trailing(self):
        source = 'foo(a, b)\n'
        self.assertEqual(fix_trailing_commas(source), source)

    def test_subscript(self):
        source = textwrap.dedent("""\
            x = arr[
                0, 1
            ]
        """)
        self.assertEqual(fix_trailing_commas(source), source)


class TestNested(unittest.TestCase):

    def test_nested_calls(self):
        source = textwrap.dedent("""\
            result = outer(
                inner(a, b, c),
                inner(d, e, f)
            )
        """)
        expected = textwrap.dedent("""\
            result = outer(
                inner(a, b, c),
                inner(d, e, f),
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_nested_both_multiline(self):
        source = textwrap.dedent("""\
            result = outer(
                inner(
                    a, b
                )
            )
        """)
        expected = textwrap.dedent("""\
            result = outer(
                inner(
                    a, b,
                ),
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_list_inside_call(self):
        source = textwrap.dedent("""\
            foo(
                [
                    1, 2, 3
                ]
            )
        """)
        expected = textwrap.dedent("""\
            foo(
                [
                    1, 2, 3,
                ],
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)


class TestUnhug(unittest.TestCase):

    def test_unhug_close(self):
        source = textwrap.dedent("""\
            foo(
                a,
                b, c)
        """)
        expected = textwrap.dedent("""\
            foo(
                a,
                b, c,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_unhug_open(self):
        source = textwrap.dedent("""\
            foo(a,
                b, c
            )
        """)
        expected = textwrap.dedent("""\
            foo(
                a,
                b, c,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)


class TestIndentation(unittest.TestCase):

    def test_closing_brace_dedented(self):
        source = textwrap.dedent("""\
            def load(root: str, date_from: dt.date,
                     ) -> dict[dt.date, float]:
                pass
        """)
        expected = textwrap.dedent("""\
            def load(
                root: str, date_from: dt.date,
            ) -> dict[dt.date, float]:
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_indented_call(self):
        source = textwrap.dedent("""\
            if True:
                foo(
                    a, b
                )
        """)
        expected = textwrap.dedent("""\
            if True:
                foo(
                    a, b,
                )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)


class TestIdempotent(unittest.TestCase):
    """Applying fix_trailing_commas twice should produce the same result."""

    def test_idempotent_call(self):
        source = textwrap.dedent("""\
            foo(
                a, b
            )
        """)
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)

    def test_idempotent_removal(self):
        source = 'foo(a, b,)\n'
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)


class TestWindowsNewlines(unittest.TestCase):
    """The original bug: \r\n should not become \r\r\n."""

    def test_crlf_preserved(self):
        source = "foo(\r\n    a, b\r\n)\r\n"
        expected = "foo(\r\n    a, b,\r\n)\r\n"
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_no_double_cr(self):
        source = "foo(\r\n    a, b\r\n)\r\n"
        result = fix_trailing_commas(source)
        self.assertNotIn('\r\r', result)


class TestAnnotatedDef(unittest.TestCase):
    """The yapf cycle case: annotated function defs with continuation indent."""

    def test_yapf_continuation_indent_fixed(self):
        """yapf produces continuation-indent; we dedent the close paren."""
        source = textwrap.dedent("""\
            def load_daily_sigma(root: str, date_from: dt.date,
                                 ) -> dict[dt.date, float]:
                pass
        """)
        expected = textwrap.dedent("""\
            def load_daily_sigma(
                root: str, date_from: dt.date,
            ) -> dict[dt.date, float]:
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_idempotent_after_fix(self):
        """Once fixed, running again should produce identical output."""
        source = textwrap.dedent("""\
            def load_daily_sigma(root: str, date_from: dt.date,
                                 ) -> dict[dt.date, float]:
                pass
        """)
        once = fix_trailing_commas(source)
        twice = fix_trailing_commas(once)
        self.assertEqual(once, twice)


class TestDecorator(unittest.TestCase):

    def test_decorated_call(self):
        source = textwrap.dedent("""\
            @decorator(
                arg1, arg2
            )
            def foo():
                pass
        """)
        expected = textwrap.dedent("""\
            @decorator(
                arg1, arg2,
            )
            def foo():
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), expected)


class TestKeywordContexts(unittest.TestCase):
    """Parenthesized expressions after keywords should not get commas."""

    def test_return_paren_expr(self):
        source = textwrap.dedent("""\
            return (
                long_expr + other
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_return_tuple(self):
        source = textwrap.dedent("""\
            return (
                a, b
            )
        """)
        expected = textwrap.dedent("""\
            return (
                a, b,
            )
        """)
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_assert_single_value(self):
        source = textwrap.dedent("""\
            assert (
                condition
            )
        """)
        self.assertEqual(fix_trailing_commas(source), source)

    def test_if_paren(self):
        source = textwrap.dedent("""\
            if (
                condition
            ):
                pass
        """)
        self.assertEqual(fix_trailing_commas(source), source)


if __name__ == '__main__':
    unittest.main()
