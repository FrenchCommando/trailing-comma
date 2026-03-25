# trailing-comma

Add and remove trailing commas in Python source files.

A minimal replacement for [add-trailing-comma](https://github.com/asottile/add-trailing-comma),
built on [tokenize-rt](https://github.com/asottile/tokenize-rt). No AST — walks the token stream directly.

The original only exposes file and stdin interfaces — no way to work on strings directly.
Exposing `fix_trailing_commas(source)` as the core API makes it usable as a library and
directly testable, which revealed a latent bug in the original's unhug re-indentation logic.

## Install

```
pip install trailing-comma
```

For development (includes build and twine for publishing):

```
pip install -e ".[dev]"
```

## Usage

Rewrite files in place:

```
trailing-comma file1.py file2.py
```

From stdin (no arguments):

```
echo "foo(
    a, b
)" | trailing-comma
```

As a library:

```python
from trailing_comma import fix_trailing_commas

result = fix_trailing_commas(source)
```

## What it does

- **Adds** trailing commas to multi-line calls, defs, imports, lists, dicts, sets, and tuples
- **Removes** trailing commas from single-line constructs (preserves single-element tuples)
- **Unhugs** content from braces and fixes closing brace indentation

## What it skips

Generators, comprehensions, class bases, subscripts, parenthesized expressions.

