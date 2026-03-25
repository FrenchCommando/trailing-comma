"""CLI entry point for trailing-comma."""

import argparse
import sys

from trailing_comma._core import fix_trailing_commas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Add/remove trailing commas')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    if not args.filenames:
        contents = sys.stdin.buffer.read().decode()
        sys.stdout.buffer.write(fix_trailing_commas(contents).encode())
        return 0

    ret = 0
    for filename in args.filenames:
        ret |= _fix_file(filename)
    return ret


def _fix_file(filename: str) -> int:
    with open(filename, 'rb') as handle:
        original = handle.read()

    try:
        contents = original.decode()
    except UnicodeDecodeError:
        print(f'{filename}: non-utf-8 (skipped)', file=sys.stderr)
        return 1

    result = fix_trailing_commas(contents)

    if result != contents:
        print(f'Rewriting {filename}', file=sys.stderr)
        with open(filename, 'wb') as handle:
            handle.write(result.encode())
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
