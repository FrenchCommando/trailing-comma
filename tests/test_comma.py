"""Tests for adding and removing trailing commas."""

import unittest

from trailing_comma import fix_trailing_commas


class TestAddComma(unittest.TestCase):
    """Multi-line constructs that should get a trailing comma added."""

    def test_function_call(self):
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

    def test_function_call_already_has_comma(self):
        source = """\
            foo(
                a, b,
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_function_def(self):
        source = """\
            def foo(
                a, b
            ):
                pass
        """
        expected = """\
            def foo(
                a, b,
            ):
                pass
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_async_def(self):
        source = """\
            async def foo(
                a, b
            ):
                pass
        """
        expected = """\
            async def foo(
                a, b,
            ):
                pass
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_import(self):
        source = """\
            from os.path import (
                join,
                exists
            )
        """
        expected = """\
            from os.path import (
                join,
                exists,
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_list(self):
        source = """\
            x = [
                1, 2, 3
            ]
        """
        expected = """\
            x = [
                1, 2, 3,
            ]
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_dict(self):
        source = """\
            x = {
                "a": 1,
                "b": 2
            }
        """
        expected = """\
            x = {
                "a": 1,
                "b": 2,
            }
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_set(self):
        source = """\
            x = {
                1, 2, 3
            }
        """
        expected = """\
            x = {
                1, 2, 3,
            }
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_tuple(self):
        source = """\
            x = (
                1, 2, 3
            )
        """
        expected = """\
            x = (
                1, 2, 3,
            )
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_decorated_call(self):
        source = """\
            @decorator(
                arg1, arg2
            )
            def foo():
                pass
        """
        expected = """\
            @decorator(
                arg1, arg2,
            )
            def foo():
                pass
        """
        self.assertEqual(fix_trailing_commas(source), expected)

    def test_return_tuple(self):
        source = """\
            return (
                a, b
            )
        """
        expected = """\
            return (
                a, b,
            )
        """
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


if __name__ == '__main__':
    unittest.main()
