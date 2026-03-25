"""Tests for the CLI entry point."""

import io
import os
import tempfile
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


class TestCLIFile(unittest.TestCase):
    """File arguments rewrite in place."""

    def _write_tmp(self, content: bytes) -> str:
        fd, path = tempfile.mkstemp(suffix='.py')
        os.write(fd, content)
        os.close(fd)
        return path

    def test_file_rewritten(self):
        path = self._write_tmp(b'foo(\n    a, b\n)\n')
        ret = main([path])
        with open(path, 'rb') as handle:
            result = handle.read()
        os.unlink(path)
        self.assertEqual(ret, 1)
        self.assertEqual(result, b'foo(\n    a, b,\n)\n')

    def test_file_unchanged(self):
        path = self._write_tmp(b'foo(a, b)\n')
        ret = main([path])
        with open(path, 'rb') as handle:
            result = handle.read()
        os.unlink(path)
        self.assertEqual(ret, 0)
        self.assertEqual(result, b'foo(a, b)\n')

    def test_exit_code_multiple_files(self):
        changed = self._write_tmp(b'foo(\n    a, b\n)\n')
        unchanged = self._write_tmp(b'foo(a, b)\n')
        ret = main([changed, unchanged])
        os.unlink(changed)
        os.unlink(unchanged)
        self.assertEqual(ret, 1)


if __name__ == '__main__':
    unittest.main()
