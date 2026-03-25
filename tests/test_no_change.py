"""Tests for constructs that should not be modified."""

import unittest

from trailing_comma import fix_trailing_commas


class TestNoChange(unittest.TestCase):

    def test_generator(self):
        source = """\
            sum(
                x for x in range(10)
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_list_comprehension(self):
        source = """\
            x = [
                item
                for item in things
            ]
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_dict_comprehension(self):
        source = """\
            x = {
                k: v
                for k, v in items
            }
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_parenthesized_expression(self):
        source = """\
            x = (
                long_expr + other
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_class_bases(self):
        source = """\
            class Foo(
                Bar, Baz
            ):
                pass
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_empty_call(self):
        source = """\
            foo(
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_single_line_no_trailing(self):
        source = 'foo(a, b)\n'
        self.assertEqual(fix_trailing_commas(source), source)

    def test_subscript(self):
        source = """\
            x = arr[
                0, 1
            ]
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_return_paren_expr(self):
        source = """\
            return (
                long_expr + other
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_assert_single_value(self):
        source = """\
            assert (
                condition
            )
        """
        self.assertEqual(fix_trailing_commas(source), source)

    def test_if_paren(self):
        source = """\
            if (
                condition
            ):
                pass
        """
        self.assertEqual(fix_trailing_commas(source), source)


if __name__ == '__main__':
    unittest.main()
