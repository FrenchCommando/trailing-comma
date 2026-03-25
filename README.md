# trailing-comma

Add and remove trailing commas in Python source files.

A minimal replacement for [add-trailing-comma](https://github.com/asottile/add-trailing-comma),
built on [tokenize-rt](https://github.com/asottile/tokenize-rt). No AST — walks the token stream directly.

## Install

```
pip install trailing-comma
```

## Usage

Rewrite files in place:

```
trailing-comma file1.py file2.py
```

Read stdin, write stdout:

```
trailing-comma -
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
