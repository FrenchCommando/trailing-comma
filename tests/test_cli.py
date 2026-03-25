"""Tests for the CLI entry point."""

import io
import unittest
import unittest.mock

from trailing_comma.__main__ import main


class TestCLIStdin(unittest.TestCase):
    """No arguments reads stdin, writes stdout."""

    def _run_stdin(self, source: bytes) -> tuple[int, bytes]:
        stdin_buf = io.BytesIO(source)
        stdout_buf = io.BytesIO()
        with (
            unittest.mock.patch('sys.stdin', buffer=stdin_buf),
            unittest.mock.patch('sys.stdout', buffer=stdout_buf),
        ):
            ret = main([])
        return ret, stdout_buf.getvalue()

    def test_stdin_multiline(self):
        ret, output = self._run_stdin(b'foo(\n    a, b\n)\n')
        self.assertEqual(ret, 0)
        self.assertEqual(output, b'foo(\n    a, b,\n)\n')

    def test_stdin_no_change(self):
        source = b'foo(a, b)\n'
        ret, output = self._run_stdin(source)
        self.assertEqual(ret, 0)
        self.assertEqual(output, source)


if __name__ == '__main__':
    unittest.main()
